import math
import numpy as np
import matplotlib.pyplot as plt

array = np.linspace(-1280,1280,128)

# Larmor frequency at 0.55T (MHz) : 23.419
# time-bw product 2.7
# half-width central lobe to = 1/bw = T/bw-time product
# to = 2560 / 2.7

# Number of lobes N = T/2to
# N = 2560/2*to
# print(N)

# Alpha for Hanning 0.5, for Hamming 0.46
# alpha = 0.5

# amplitude = 230

# index = 0
# for element in array:
#     # if element == 0:
#     #     value = amplitude   
#     value = (amplitude * to) * ((1-alpha) + alpha*math.cos(math.pi * element / (N * to)))*math.sin(math.pi*element/to)/(math.pi*element)
#     array[index] = abs( value )
#     index=index+1

# plt.plot(np.linspace(-1280,1280,128), array)
# plt.show()

####################################################

duration = 2.560E-3
bwTimeProduct = 2.7
sliceThickness = 5E-3
dwellTime = 20E-6
apodization = 0.6
flipAngle = 15 * np.pi / 180

# Info for rf calculation
bandWidth = bwTimeProduct/duration
# print("bw "+str(bandWidth))
numberOfPoints = int(duration/dwellTime)
# print("nbOfPoints "+str(numberOfPoints))

# Info for sliceselction gradient
sliceSelectionGradientAmplitude = bandWidth / sliceThickness
# print("sSelAmpl "+str(sliceSelectionGradientAmplitude))
sliceSelectionGradientArea = sliceSelectionGradientAmplitude * duration
# print("sSelArea "+str(sliceSelectionGradientAmplitude))

# Designing rf waveform enveloppe
baseArray = (np.arange(1, numberOfPoints + 1) - 0.5) * dwellTime
centeredBaseArray = baseArray - duration/2
# print("centBaseArray "+str(centeredBaseArray))
window = np.cos(2*np.pi*centeredBaseArray/duration)
window = 1 - apodization + apodization * window
rfWaveform = window * ( np.sin(bandWidth*centeredBaseArray)/(bandWidth*centeredBaseArray) )
flip = np.sum(rfWaveform) * dwellTime * 2 * np.pi
rfWaveform = rfWaveform * flipAngle / flip


phaseArray = np.zeros(128)
index = 0
for phase in phaseArray:
    if(index<17 or index>111):
        phaseArray[index] = 3.14159
    index += 1

realPartSum = 0
imaginaryPartSum = 0
for index in range(0, 128):
    realPartSum += rfWaveform[index] * np.cos(phaseArray[index])
    imaginaryPartSum += rfWaveform[index] * np.sin(phaseArray[index])

amplitudeIntegral = np.sqrt(pow(realPartSum,2) + pow(imaginaryPartSum,2))
print("amplitudeIntegral " + str(amplitudeIntegral))

counter =0
for elem in rfWaveform:
    print("                "+str("{0:.5f}".format(abs(elem)/np.max(rfWaveform)))+", ")
    print("                "+str("{0:.5f}".format(phaseArray[counter]))+", ")
    counter +=1
print(counter)

plt.plot(baseArray*1000, rfWaveform)
plt.show()

