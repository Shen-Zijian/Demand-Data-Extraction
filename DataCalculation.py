import numpy as np
import sys
import time
import json


def data_calculaton(a, b):
	c = a * b
	return c


if __name__ == '__main__':
	start_time = time.time()

	# Open the JSON file and load the matrices
	with open(sys.argv[1], 'r') as f:
		data = json.load(f)
	a = np.array(data['a'])
	b = np.array(data['b'])

	result = data_calculaton(a, b).tolist()  # convert numpy array to list
	end_time = time.time()
	print("Python Execution time:", end_time - start_time)

	# Save the result as JSON
	with open('result.json', 'w') as f:
		json.dump(result, f)