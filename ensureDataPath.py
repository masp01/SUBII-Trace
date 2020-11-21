import os
from tkinter import filedialog
from tkinter import messagebox
from dataPath import trialToDirectory

class ensureDataPath:
	"""
	Validate the contour data and image directories for biofilm analysis.

	Directories are stored in dataPath.py. If the directories do not exist,
	the user will be prompted to choose directories.

	Notes
	-----
	Paths to contour data and images are stored in self.paths

	These paths still require formatting, and image paths are expected to be given to
	pims.ImageSequence().

	Examples
	--------
	>>> from ensureDataPath import ensureDataPath
	>>> paths = ensureDataPath().paths

	paths.contours[4] contains the path to contour directories for Trial 4
	paths.images[4] contains the path to Trial 4 images

	See examples of full usage in Supervise.py or RoughnessCalc.py
	"""
	def __init__(self):
		# For each trial listed, a contour and image directory will be validated.
		# If you add a trial, be sure to update self.templates with the appropriate
		# key:value pairs
		self.trials = [4,5]

		self.prompts = {
		'contours':'Cannot find a contour directory for trial {}. Choose directory?',
		'images':'Cannot find an image directory for trial {}. Choose directory?'
		}

		self.templates = {
		'contours':{
		4:'trial4xy{0:02d}/',
		5:'trial5xy{0:02d}/'
		},
		'images':{
		4:'*trial4*xy{0:02d}*.tif',
		5:'*trial5*xy{0:02d}*.tif'
		}
		}

		self.pairTemplate = "\n        {0}:'{1}',"
		
		self.paths = trialToDirectory()
		self.setPaths(force=False)

	def promptDirectory(self, pathCollection, key):
		result = messagebox.askokcancel(message=self.prompts[pathCollection].format(key))
		if result == False: # Cancel or X was clicked by the user
			return False
		else:
			directory = filedialog.askdirectory()
			return directory
	
	def setPaths(self, force=True):
		defaultLines = [
		"class trialToDirectory:",
		"    def __init__(self):",
		"        self.contours = {$contours_pairs$",
		"        }",
		"",
		"        self.images = {$images_pairs$",
		"        }"
		]
		
		fileString = '\n'.join(defaultLines)

		# go through each property (path dictionary) of trialToDirectory
		# and test if each of the directories in the dictionary exist
		# otherwise prompt the user to choose a directory
		# then rewrite the file dataPath.py to reflect these changes

		# self.paths contains full file paths
		for pathCollection, pathDict in vars(self.paths).items():
			useAll_notAsked = True
			pathForAll = ''
			pairs = ''
			for key in self.trials:
				validKey = True
				try:
					current_dir = pathDict[key]
				except KeyError:
					validKey = False
					current_dir = ''
				if force or not os.path.exists(current_dir) or not validKey:
					if pathForAll == '':
						directory = self.promptDirectory(pathCollection, key)
						if directory == False: # user chose not to pick a directory
							return
						if useAll_notAsked:
							useAllResult = messagebox.askyesno(message='Use this directory for all {}?'.format(pathCollection))
							if useAllResult:
								pathForAll = directory
							useAll_notAsked = False
					else:
						directory = pathForAll
				else:
					directory = str(current_dir)				
				fullPath = os.path.join(directory, self.templates[pathCollection][key])
				fullPath = fullPath.replace('\\', '/') # technically cheating, but Python allows Windows paths to use '/'
				directory = directory.replace('\\', '/') # ''
				getattr(self.paths, pathCollection)[key] = fullPath
				pairs += self.pairTemplate.format(key, directory)
			fileString = fileString.replace('${0}_pairs$'.format(pathCollection), pairs)
	
		with open('dataPath.py', 'w') as data_file:
			data_file.write(fileString)