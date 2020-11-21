This repository is specialized for data from a previous experiment performed at Syracuse University. Some of that data is included as an example.
If you would like to adjust this code for your own data, please contact me at masp01@syr.edu
Syracuse University BioInspired Institute - https://bioinspired.syr.edu/

Set up supervised biofilm tracing from scratch
----------------------------------------------

Install Anaconda (a Python distribution)
- Download Anaconda Individual Edition at https://www.anaconda.com/products/individual
- Choose the Python 3.7 version
- Run the installer
	
Install prerequisite packages
- Open the Anaconda Command Prompt
- Type the following and hit enter for each line:
`conda install -c conda-forge pims`
`pip install opencv-contrib-python`

Run the scripts
- Open the Anaconda Command Prompt
- Navigate to the directory containing the scripts using `cd`
- Type the following and hit enter to enter interactive mode:
`ipython --pylab`
- Type the following and hit enter to run the script:
`run Supervise`
	
How to use the software
----------------------------

- You should be prompted to choose image and contour directories
  - This will only happen on your first launch
  - In the folder containing the scripts, choose the 'Images' folder when prompted
  - Choose 'Yes' to use this directory for all images
  - In the folder containing the scripts, choose the 'Contours' folder when prompted
  - Choose 'Yes' to use this directory for all contours
- An image and a GUI should appear
- The image is one frame of a monochrome video of biofilm growth
  - A blue transparent line shows where the predicted biofilm boundary is
	
Adjusting prediction parameters
- The prediction algorithm contains four steps:
1. Detect edges
- a minumum and maximum gray value (0-255) expected for edges is used
2. Fill between edges (closing broken lines)
3. Trace contours around all closed shapes
- The longest contour is automatically chosen
4. Split contours into segments at the image's edges
- The segment with the longest edge-to-edge distance is the predicted boundary
- A radio button shows either the image, the detected edges, or the filled shapes (which define the contours)
- Adjust the edgeMin and edgeMax properties, then click 'Redo Edges' to troubleshoot edge detection
  - edgeMin can sometimes be set higher than edgeMax with useful effects
- Sometimes the wrong contour or segment is automatically chosen
- Choose the next longest contour by clicking 'Next Contour >'
  - Go back by clicking '<'
  - Contours that do not touch the edge are skipped
  - You can also use 'f' as a hotkey to go to the next contour
- Choose the next longest segment within the chosen contour by clicking 'Next Segment >'
  - Go back by clicking '<'

Manually changing the boundary
- If a boundary contains just a small error, like a bump due to a speck of dust near the boundary, these can be corrected by hand
- Click a point on the blue line
- Draw the corrected line, holding down the left mouse button
- Release the left mouse button while the cursor is still somewhere on the blue line (or outside the image)
- The newly drawn line will be inserted in, removing the error
  - If you release the mouse button while off the blue line, the newly drawn line will be ignored
  - Corrections will also be accepted if the mouse leaves the image edges
  - Go forward and back one frame to reset your changes
- NOTE: The software expects manual changes to be small
  - If you make a large change, unexpected results may occur
  - Try to break up large changes into a series of small changes
		
Saving output
- When the boundary for each frame is acceptable, press 's'
- A datafile containing pairs of xy coordinates will be saved to the output directory you chose
- Automatic versus manually entered points are distinguishable by data precision
  - Manually entered points will have more precise coordinates
- If a frame has output that has already been saved, a warning will appear in the Anaconda Command Prompt
- Saving again will replace the old data

Navigation
- Advance to the next frame by clicking 'Next Frame >'
  - Go back by clicking '<'
  - You can also move frames with the right and left arrow keys
- Each biofilm growth video is indexed by a Trial number and an xy number
- Choose a new Trial and xy number and click 'Load' to open a new video
- The data given with this folder contains:
  - Trial 4: xy09, xy10
  - Trial 5: xy09, xy10
- Clicking the magnifying glass on the image will enter zoom mode
  - Draw a rectangular region to zoom into that region
  - You can go back to the previous zoom state by clicking the back or Home button
  - Remember to exit zoom mode to allow manual boundary adjustments
		
Hotkeys
- NOTE: Hotkeys will only work if the image (not the GUI) is in focus
- Right	: Next frame
- Left	: Previous frame
- f 	: Next contour
- s		: Save contour