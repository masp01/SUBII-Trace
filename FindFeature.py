import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pims # conda install -c conda-forge pims
import cv2 # pip install opencv-contrib-python
from ensureDataPath import ensureDataPath
from which import which

class FindBoundary:
	def __init__(self, i, img, edgeMin, edgeMax, boost=1):
		self.frameIndex = i
		self.img = img
		#self.corner = corner
		self.edgeMin = edgeMin
		self.edgeMax = edgeMax
		self.height, self.width = np.shape(self.img)
		self.edges = None
		self.fill = None
		self.contours = []
		self.segments = []
		self.c = 0 # which contour has been split into segments

		# Canny edge detection with OpenCV requires 8-bit images
		if isinstance(self.img[0][0], np.uint16):
			# factor to boost depth on low brightness areas,
			# clipping large values at a maximum ceiling
			self.boost = boost
			self.img *= self.boost
			self.img = (self.img/256).astype(np.uint8)

		self.findBoundary(self.edgeMin, self.edgeMax)

	def contourToXY(self, contour):
		xs = np.array([e[0][0] for e in contour])
		ys = np.array([e[0][1] for e in contour])
		return xs, ys

	def splitSegments(self, contour):
		xs, ys = contour

		# Find indices of all points on the edge
		splits = np.unique(np.concatenate((which(xs == 0), which(xs == self.width-1), which(ys == 0), which(ys == self.height-1))))
		
		# Collect pairs of indices where segments begin and end
		segmentIndices = []
		for j in range(len(splits)):
			if j == len(splits) - 1:
				comp = splits[0] + len(xs)
			else:
				comp = splits[j+1]
			if comp - splits[j] > 1:
				segmentIndices.append((splits[j], splits[(j+1) % len(splits)]))

		# Save xy coordinates of each segment
		# and the Euclidean distance between the segments' ends
		segments = []
		endToEndDists = []
		for pair in segmentIndices:
			i, f = pair
			if i > f:
				xseg = np.concatenate((xs[i:], xs[:f+1]))
				yseg = np.concatenate((ys[i:], ys[:f+1]))
			else:
				xseg = xs[i:(f+1)]
				yseg = ys[i:(f+1)]
			segments.append((xseg, yseg))
			endToEndDists.append(np.sqrt((xs[f] - xs[i])**2 + (ys[f] - ys[i])**2))

		# Sort segments by end-to-end distance (greatest first)
		# and return the xy coordinates of each segment
		segments = np.array(segments)[np.argsort(endToEndDists)[::-1]]
		return segments

	def findBoundary(self, edgeMin, edgeMax):
		# update edge detection bounds 
		self.edgeMin = edgeMin
		self.edgeMax = edgeMax

		# Run canny edge detection
		self.edges = cv2.Canny(self.img, self.edgeMin, self.edgeMax)

		# Close broken lines using the morphological "closing" operation
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
		self.fill = cv2.morphologyEx(self.edges, cv2.MORPH_CLOSE, kernel)

		# Identify the individual contours and sort by length (longest first)
		contourPoints = cv2.findContours(self.fill, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
		contourLengths = np.array([len(c) for c in contourPoints])
		contourPoints = np.array(contourPoints)[np.argsort(contourLengths)[::-1]]

		# Store xy coordinates of the contours
		self.contours = [self.contourToXY(c) for c in contourPoints]

		# Find the the longest contour that touches the image edges
		# and split it into segments that touch the edges
		for i in range(len(self.contours)):
			self.segments = self.splitSegments(self.contours[i])
			self.c = i
			if len(self.segments) > 0:
				break

	# Convenience functions for plotting contours and segments
	def showTop(self, n=10):
		if n > len(self.contours):
			print ("Showing all {0} contours".format(len(self.contours)))
			n = len(self.contours)
		plt.imshow(self.img, cmap='gray')
		for c in self.contours[:n]:
			plt.plot(*c)

	def showContour(self, i=0):
		plt.imshow(self.img, cmap='gray')
		plt.plot(*self.contours[i])

	def showSegment(self, i=0):
		print("Showing segment {0} of {1}".format(i, len(self.segments)))
		plt.imshow(self.img, cmap='gray')
		plt.plot(*self.segments[i])

class Boundaries:
	def __init__(self, trial, xy, edgeMin=10, edgeMax=10, boost=1):
		paths = ensureDataPath().paths
		imgPath = paths.images[trial].format(xy)
		self.images = pims.ImageSequence(imgPath, as_grey=True)
		self.frames = []
	
		for i,img in enumerate(self.images):
			boundary = FindBoundary(i, img, edgeMin, edgeMax, boost)
			self.frames.append(boundary)
			# Display all predicted boundaries
			# plt.plot(*boundary.segments[0], color='yellow')