import numpy as np

def which(booleanArray):
	"""Returns the indices of which values in the given array are true"""
	if isinstance(booleanArray, bool):
		booleanArray = [booleanArray]
	return np.array(range(len(booleanArray)))[booleanArray]