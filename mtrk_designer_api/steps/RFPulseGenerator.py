import math
import numpy as np
import matplotlib.pyplot as plt

array = np.linspace(-1280,1280,128)

# Larmor frequency at 0.55T (MHz) : 23.419
# time-bw product 2.7
# half-width central lobe to = 1/bw = T/bw-time product
to = 2560 / 2.7

# Number of lobes N = T/2to
N = 2560/2*to
print(N)

# Alpha for Hanning 0.5, for Hamming 0.46
alpha = 0.5

amplitude = 230

index = 0
for element in array:
    # if element == 0:
    #     value = amplitude   
    value = (amplitude * to) * ((1-alpha) + alpha*math.cos(math.pi * element / (N * to)))*math.sin(math.pi*element/to)/(math.pi*element)
    array[index] = abs( value )
    index=index+1

plt.plot(np.linspace(-1280,1280,128), array)
plt.show()