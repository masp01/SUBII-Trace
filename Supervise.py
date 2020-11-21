import numpy as np
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from FindFeature import Boundaries
from ensureDataPath import ensureDataPath
import matplotlib.pyplot as plt
import os

class App:
	def __init__(self):
		# file access
		self.contourFile = 'trial{0}xy{1:02d}_{2:02d}.txt'
		self.paths = ensureDataPath().paths

		self.root = Tk()		# application window
		self.i = 0				# frame index
		self.c = 0				# contour index
		self.j = 0				# segment index
		self.xmin = np.inf		# display limits
		self.xmax = -1			# ''
		self.ymin = np.inf		# ''
		self.ymax = -1			# ''
		self.drawState = False	# is the user drawing points?
		self.drawnLine = None	# matplotlib artist of user-drawn line
		self.drawnXs = []		# coordinates of user-drawn line
		self.drawnYs = []		# ''

		# Calculate boundary predictions
		self.trial = 4
		self.xy = 9
		self.b = Boundaries(trial=self.trial, xy=self.xy, edgeMin=50, edgeMax=50, boost=5)
		self.c = self.b.frames[self.i].c
		
		# Store user-drawn points
		self.boundaryLine = None
		self.boundaryXs = []
		self.boundaryYs = []
		self.insertionIndices = []

		# Disable some default hotkeys
		if 's' in plt.rcParams['keymap.save']:
			plt.rcParams['keymap.save'].remove('s')
		if 'f' in plt.rcParams['keymap.fullscreen']:
			plt.rcParams['keymap.fullscreen'].remove('f')

		# Create all frames
		TrialControls = Frame(self.root)
		ViewControls = Frame(self.root)
		EdgeControls = Frame(self.root)
		FrameControls = Frame(self.root)
		ContourControls = Frame(self.root)
		SegmentControls = Frame(self.root)
		
		# Organize frames vertically in order
		TrialControls.pack()
		ViewControls.pack()
		EdgeControls.pack()
		FrameControls.pack()
		ContourControls.pack()
		SegmentControls.pack()

		# Widgets in TrialControls
		Label(TrialControls, text='Trial').grid(row=0)
		self.trialEntry = Entry(TrialControls, width=5)
		self.trialEntry.insert(0, 4)	# Default value for 'trial'
		self.trialEntry.grid(row=0, column=1)
		Label(TrialControls, text='xy').grid(row=0, column=2)
		self.xyEntry = Entry(TrialControls, width=5)
		self.xyEntry.insert(0, 9)		# Default value for 'xy'
		self.xyEntry.grid(row=0, column=3)
		Button(TrialControls, text="Load", command=self.loadData).grid(row=0, column=4)

		# Widgets in EdgeControls
		Label(EdgeControls, text="edgeMin").grid(row=0)
		self.edgeMinEntry = Entry(EdgeControls, width=5)
		self.edgeMinEntry.insert(0, 50)
		self.edgeMinEntry.grid(row=0, column=1)
		Label(EdgeControls, text="edgeMax").grid(row=1)
		self.edgeMaxEntry = Entry(EdgeControls, width=5)
		self.edgeMaxEntry.insert(0, 50)
		self.edgeMaxEntry.grid(row=1, column=1)
		Button(EdgeControls, text="Redo Edges", command=self.redoEdges).grid(row=0, column=2, rowspan=2)

		# Widgets in ViewControls
		self.viewMode = StringVar()
		self.viewMode.set('img')
		Radiobutton(ViewControls, text="Image", variable=self.viewMode, value='img', command=self.showFrame).pack()
		Radiobutton(ViewControls, text="Edges", variable=self.viewMode, value='edges', command=self.showFrame).pack()
		Radiobutton(ViewControls, text="Fill", variable=self.viewMode, value='fill', command=self.showFrame).pack()

		# Widgets in FrameControls
		prevFrameButton = Button(FrameControls, text="<", command=lambda: self.onClickFrame(-1))
		nextFrameButton = Button(FrameControls, text="Next Frame >", command=lambda: self.onClickFrame(1))
		self.frameText = StringVar()
		self.frameText.set("{0}/{1}".format(self.i + 1, len(self.b.frames)))
		Label(FrameControls, textvariable=self.frameText).pack(side=BOTTOM)
		prevFrameButton.pack(side=LEFT)
		nextFrameButton.pack(side=LEFT)

		# Widgets in ContourControls
		prevContourButton = Button(ContourControls, text="<", command=lambda: self.onClickContour(-1))
		nextContourButton = Button(ContourControls, text="Next Contour >", command=lambda: self.onClickContour(1))
		self.contourText = StringVar()
		self.contourText.set("{0}/{1}".format(self.c + 1, len(self.b.frames[self.i].contours)))
		Label(ContourControls, textvariable=self.contourText).pack(side=BOTTOM)
		prevContourButton.pack(side=LEFT)
		nextContourButton.pack(side=LEFT)

		# Widgets in SegmentControls
		prevSegmentButton = Button(SegmentControls, text="<", command=lambda: self.onClickSegment(-1))
		nextSegmentButton = Button(SegmentControls, text="Next Segment >", command=lambda: self.onClickSegment(1))
		self.segmentText = StringVar()
		self.segmentText.set("{0}/{1}".format(self.j + 1, len(self.b.frames[self.i].segments)))
		Label(SegmentControls, textvariable=self.segmentText).pack(side=BOTTOM)
		nextSegmentButton.pack(side=RIGHT)
		prevSegmentButton.pack(side=RIGHT)

		self.fig, self.ax = plt.subplots()
		self.showFrame()
		self.fig.canvas.mpl_connect('pick_event', self.onPickDataPoint) # Enable picking data points
		self.fig.canvas.mpl_connect('button_press_event', self.onClick)
		self.fig.canvas.mpl_connect('button_release_event', self.onRelease)
		self.fig.canvas.mpl_connect('axes_leave_event', self.onLeaveAxes)
		self.fig.canvas.mpl_connect('key_press_event', self.onKey)
		plt.connect('motion_notify_event', self.drawPoints)
		plt.show()
		
		self.root.mainloop()

	def showFrame(self):
		# Get the coordinates of the predicted boundary
		xs, ys = self.b.frames[self.i].segments[self.j]
		self.boundaryXs = xs
		self.boundaryYs = ys

		# Set the display limits
		padding = 20
		xmin = min(xs) - padding
		self.xmin = min(xmin, self.xmin)
		self.xmin = max(0, self.xmin)
		xmax = max(xs) + padding
		self.xmax = max(xmax, self.xmax)
		self.xmax = min(self.b.frames[self.i].width - 1, self.xmax)
		ymin = min(ys) - padding
		self.ymin = min(ymin, self.ymin)
		self.ymin = max(0, self.ymin)
		ymax = max(ys) + padding
		self.ymax = max(ymax, self.ymax)
		self.ymax = min([self.b.frames[self.i].height - 1, self.ymax])
		
		# Display the frame and predicted boundary
		self.ax.clear()
		displayData = getattr(self.b.frames[self.i], self.viewMode.get())
		self.ax.imshow(displayData, cmap='gray')
		self.boundaryLine, = self.ax.plot(xs, ys, linewidth=4, color='#1f77b460', picker=5) # tolerance of 5 pixels for clicking data points
		plt.xlim(self.xmin, self.xmax)
		plt.ylim(self.ymax, self.ymin)
		self.fig.canvas.draw() # This line is necessary to update the figure

	def rollback(self, prevTrial, prevXy):
		self.trial = prevTrial
		self.xy = prevXy
		self.trialEntry.delete(0, END)
		self.trialEntry.insert(0, '{}'.format(self.trial))
		self.xyEntry.delete(0, END)
		self.xyEntry.insert(0, '{}'.format(self.xy))

	def loadData(self):
		prevTrial = self.trial
		prevXy = self.xy
		# Check that the given trial and xy are valid numbers
		try:
			self.trial = int(self.trialEntry.get())
			self.xy = int(self.xyEntry.get())
			# Check that images exist for the given trial and xy
			try:
				self.redoEdges(showFrame=False)
			except IOError:
				print("No images found for this trial and xy.")
				self.rollback(prevTrial, prevXy)
				self.redoEdges(showFrame=False)
		except ValueError:
			self.rollback(prevTrial, prevXy)

		# Print a warning if contours have already been traced for this image
		if os.path.exists(self.paths.contours[self.trial].format(self.xy) + self.contourFile.format(self.trial, self.xy, self.i+1)):
			print("This contour has already been traced. Saving will overwrite previous data.")

		# Update frame label
		self.frameText.set("{0}/{1}".format(self.i + 1, len(self.b.frames)))

		# Reset display limits
		self.xmin, self.ymin = np.inf, np.inf
		self.xmax, self.ymax = -1, -1

		# Reset to check the first frame
		self.i = 0
		self.showFrame()

	def redoEdges(self, showFrame=True):
		self.b = Boundaries(trial=self.trial, xy=self.xy, edgeMin=int(self.edgeMinEntry.get()), edgeMax=int(self.edgeMaxEntry.get()), boost=1)

		# Update labels
		self.contourText.set("{0}/{1}".format(self.c + 1, len(self.b.frames[self.i].contours)))
		self.segmentText.set("{0}/{1}".format(self.j + 1, len(self.b.frames[self.i].segments)))

		# Reset to check the first contour and segment
		self.c = self.b.frames[self.i].c
		self.j = 0
		if showFrame:
			self.showFrame()

	def onClick(self, event):
		if self.fig.canvas.manager.toolbar.mode == '':
			self.drawState = True
			self.drawPoints(event)

	def onLeaveAxes(self, event):
		if self.fig.canvas.manager.toolbar.mode != '':
			return
		if self.drawState:
			x = event.xdata
			y = event.ydata
			self.drawPoints(event)
			self.drawState = False
			if self.drawnLine is not None:
				self.drawnLine.remove()
				self.drawnLine = None
			self.fig.canvas.draw()
			if len(self.insertionIndices) == 1: # a new insertion was drawn from a boundary point to the edge of the image
				i = self.insertionIndices[0]

				# determine which end of the boundary to change
				# and add the drawn points to the end of the boundary
				if i < int(np.floor(len(self.boundaryXs)/2)):
					keptBoundaryXs = self.boundaryXs[i:]
					keptBoundaryYs = self.boundaryYs[i:]
					self.boundaryXs = np.concatenate((self.drawnXs[::-1], keptBoundaryXs))
					self.boundaryYs = np.concatenate((self.drawnYs[::-1], keptBoundaryYs))
				else:
					keptBoundaryXs = self.boundaryXs[:i+1]
					keptBoundaryYs = self.boundaryYs[:i+1]
					self.boundaryXs = np.concatenate((keptBoundaryXs, self.drawnXs))
					self.boundaryYs = np.concatenate((keptBoundaryYs, self.drawnYs))

				# redraw the boundary
				self.boundaryLine.remove()
				self.boundaryLine, = self.ax.plot(self.boundaryXs, self.boundaryYs, linewidth=4, color='#1f77b460', picker=5)
				self.fig.canvas.draw()

	def onRelease(self, event):
		if self.fig.canvas.manager.toolbar.mode != '':
			return
		self.drawPoints(event)
		self.drawState = False
		self.boundaryLine.pick(event) # run the picker
		if self.drawnLine is not None:
			self.drawnLine.remove()
			self.drawnLine = None
		#self.ax.plot(self.drawnXs, self.drawnYs, linewidth=4, color='#e4211c60')
		self.fig.canvas.draw()
		if len(self.insertionIndices) == 2: # a new insertion was drawn that touched the boundary at two points
			firstBookend = np.array(range(min(self.insertionIndices) + 1))
			secondBookend = np.array(range(max(self.insertionIndices), len(self.boundaryXs)))

			# check if points were drawn in the opposite direction of the boundary points
			defaultDist = np.sqrt((self.drawnXs[0] - self.boundaryXs[firstBookend[-1]])**2 + (self.drawnYs[0] - self.boundaryYs[firstBookend[-1]])**2)
			flippedDist = np.sqrt((self.drawnXs[0] - self.boundaryXs[secondBookend[0]])**2 + (self.drawnYs[0] - self.boundaryYs[secondBookend[0]])**2)
			if flippedDist < defaultDist:
				self.drawnXs = np.array(self.drawnXs)[::-1]
				self.drawnYs = np.array(self.drawnYs)[::-1]

			# insert the drawn points inbetween the remainder of the boundary
			self.boundaryXs = np.concatenate((self.boundaryXs[firstBookend], self.drawnXs, self.boundaryXs[secondBookend]))
			self.boundaryYs = np.concatenate((self.boundaryYs[firstBookend], self.drawnYs, self.boundaryYs[secondBookend]))
			self.boundaryLine.remove()
			self.boundaryLine, = self.ax.plot(self.boundaryXs, self.boundaryYs, linewidth=4, color='#1f77b460', picker=5)
			self.fig.canvas.draw()
		
		# Reset drawn points
		self.insertionIndices = []
		self.drawnXs = []
		self.drawnYs = []

	def drawPoints(self, event):
		if self.drawState:
			self.drawnXs.append(event.xdata)
			self.drawnYs.append(event.ydata)
			if self.drawnLine is not None:
				self.ax.lines.remove(self.drawnLine)
				self.drawnLine = None
			self.drawnLine, = self.ax.plot(self.drawnXs, self.drawnYs, linewidth=4, color='#e4211c30')
			self.fig.canvas.draw()

	def onKey(self, event):
		print(event.key)
		if event.key == 's':
			print('Got save event')
			filename = self.paths.contours[self.trial].format(self.xy) + self.contourFile.format(self.trial, self.xy, self.i+1)
			if not os.path.exists(self.paths.contours[self.trial].format(self.xy)):
				os.makedirs(self.paths.contours[self.trial].format(self.xy))
			with open(filename, 'w') as txt_file:
				for i in range(len(self.boundaryXs)):
					txt_file.write(str(self.boundaryXs[i]) + '\t' + str(self.boundaryYs[i]) + '\n')
		elif event.key == 'right':
			self.onClickFrame(1)
		elif event.key == 'left':
			self.onClickFrame(-1)
		elif event.key == 'f':
			self.onClickContour(1)

	def onPickDataPoint(self, event):
		line = event.artist
		xs = line.get_xdata()
		ys = line.get_ydata()
		indices = np.array(event.ind)
		ind = indices[int(np.floor(len(indices)/2))] # choose the index of the center point
		self.insertionIndices.append(ind)
		#points = tuple(zip(xs[ind], ys[ind]))
		#print('onpick points: {0}'.format(points))

	def onClickFrame(self, step):
		# Move one frame
		self.i += step
		self.i %= len(self.b.frames) # loop back to the first frame

		# Reset to check the first contour and segment
		self.c = self.b.frames[self.i].c
		self.b.frames[self.i].segments = self.b.frames[self.i].splitSegments(self.b.frames[self.i].contours[self.c])
		self.j = 0

		# Update labels
		self.frameText.set("{0}/{1}".format(self.i + 1, len(self.b.frames)))
		self.contourText.set("{0}/{1}".format(self.c + 1, len(self.b.frames[self.i].contours)))
		self.segmentText.set("{0}/{1}".format(self.j + 1, len(self.b.frames[self.i].segments)))

		# Reset the display limits when on the first frame
		if self.i == 0:
			self.xmin, self.ymin = np.inf, np.inf
			self.xmax, self.ymax = -1, -1

		# Print a warning if contours have already been traced for this image
		if os.path.exists(self.paths.contours[self.trial].format(self.xy) + self.contourFile.format(self.trial, self.xy, self.i+1)):
			print("This contour has already been traced. Saving will overwrite previous data.")

		# Show the frame and boundary
		self.showFrame()

	def onClickContour(self, step):
		# Move one contour
		self.c += step
		self.c %= len(self.b.frames[self.i].contours) # loop back to the first contour

		# Find the first contour that touches the image edges and split it into segments
		contourRange = np.array(range(len(self.b.frames[self.i].contours)))
		if step == 1:
			contourRange = np.concatenate((contourRange[self.c:], contourRange[:self.c]))
		else:
			contourRange = np.concatenate((contourRange[self.c::-1], contourRange[self.c+1:][::-1]))
		for thisC in contourRange:
			self.b.frames[self.i].segments = self.b.frames[self.i].splitSegments(self.b.frames[self.i].contours[thisC])
			if len(self.b.frames[self.i].segments) > 0:
				self.c = thisC
				break

		# Warn the user if no such contour is found
		if len(self.b.frames[self.i].segments) == 0:
			print("No contours found that touch the edges")
			self.b.frames[self.i].segments = [self.b.frames[self.i].contours[self.c]] # store contour coordinates anyway

		# Reset to check the first segment
		self.j = 0

		# Update labels
		self.contourText.set("{0}/{1}".format(self.c + 1, len(self.b.frames[self.i].contours)))
		self.segmentText.set("{0}/{1}".format(self.j + 1, len(self.b.frames[self.i].segments)))

		# Reset the display limits
		#self.xmin, self.ymin = np.inf, np.inf
		#self.xmax, self.ymax = -1, -1

		# Show the frame and boundary
		self.showFrame()

	def onClickSegment(self, step):
		# Move one segment
		self.j += step
		self.j %= len(self.b.frames[self.i].segments) # loop back to the first segment
		
		# Update segment label
		self.segmentText.set("{0}/{1}".format(self.j + 1, len(self.b.frames[self.i].segments)))

		# Show the frame and boundary
		self.showFrame()
		
app = App()