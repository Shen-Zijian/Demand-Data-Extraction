import numpy as np
import time

def data_calculaton(a, b):
    c = a * b
    return c

start_time = time.time()

# Convert the lists to numpy arrays
array1 = np.array(array1)
array2 = np.array(array2)

# Use the arrays passed from Java
result = data_calculaton(array1, array2).tolist()  # convert numpy array to list
end_time = time.time()
print("Python Execution time:", end_time - start_time)