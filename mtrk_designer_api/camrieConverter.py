################################################################################
### mtrk project - Conversion tool for PSUdoMRI format in Camrie.            ###
### Version 0.0.0                                                            ###
### Anais Artiges and the mtrk project team at NYU - 04/29/2024              ###
################################################################################  

from SDL_read_write.pydanticSDLHandler import *
import numpy as np
from typing import List
import matplotlib.pyplot as plt
import struct
import math
from struct import pack, unpack
import io

def camrieConverter(sequence_data):
    """
    Converts sequence data to the desired format using the CAMRIE conversion process.

    Args:
        sequence_data (str): The input sequence data in SDL format.

    Returns:
        None
    """
    ### Retrieving useful data from SDL format
    firstRawData = extractDataFromSDL(sequence_data)
    sortedLoopRanges, sortedLoopBlocks = generateLoopStructure(firstRawData)

    ### Plotting first sequence TR
    firstFormattedTRData = formattingTR(firstRawData)
    plotTR(firstFormattedTRData)

    ### Generating the full sequence timing
    sequenceTiming = generateSequenceTiming(sequence_data, sortedLoopRanges, 
                                            sortedLoopBlocks)

    ### Plotting whole sequence chronogram
    plotChronogram(sequenceTiming)

    ### Converting to PSUdoMRI format
    convertToPsudomri(sequenceTiming)
    

def extractDataFromSDL(sequence_data, counter = 0):
    """
    Extracts useful data from SDL format.

    Args:
        sequence_data (SequenceData): The SDL sequence data.
        counter (int, optional): The counter value. Defaults to 0.

    Returns:
        list: A list containing the extracted data:
            - loopCounters (list): The loop counters.
            - loopRanges (list): The loop ranges.
            - loopBlocks (list): The loop blocks.
            - repetitionTimes (list): The repetition times.
            - gradAxis (list): The gradient axes.
            - gradStartTimes (list): The gradient start times.
            - gradArrays (list): The gradient arrays.
            - rfStartTimes (list): The RF start times.
            - rfMagnArrays (list): The RF magnitude arrays.
            - rfPhaseArrays (list): The RF phase arrays.
            - adcStartTimes (list): The ADC start times.
            - adcArrays (list): The ADC arrays.
    """
    loopCounters = []
    loopRanges = []
    loopBlocks = []
    gradAxis = []
    gradArrays = []
    gradStartTimes = []
    rfMagnArrays = []
    rfPhaseArrays = []
    rfStartTimes = []
    adcArrays = []
    adcStartTimes = []
    repetitionTimes = []
    # TO DO handle RF and ADC added phases
    
    for instruction in sequence_data.instructions:
        for stepIndex in range(0, 
        len(sequence_data.instructions[instruction].steps)):
            match sequence_data.instructions[instruction].steps[stepIndex].action:
                case "loop":
                    loopCounters.append(sequence_data.instructions[instruction].steps[stepIndex].counter)
                    loopRanges.append(sequence_data.instructions[instruction].steps[stepIndex].range)
                    # TO DO: generalize for any number of steps
                    loopBlocks.append(sequence_data.instructions[instruction].steps[stepIndex].steps[0].block)
                case "grad":
                    gradAxis.append(sequence_data.instructions[instruction].steps[stepIndex].axis)
                    gradObject = sequence_data.instructions[instruction].steps[stepIndex].object
                    gradArrayName = sequence_data.objects[gradObject].array
                    gradArrayAmplitudeOption = "none"
                    if 'amplitude' in dict(sequence_data.instructions[instruction].steps[stepIndex]):
                        gradArrayAmplitudeOption = sequence_data.instructions[instruction].steps[stepIndex].amplitude
                    else:
                        pass
                    gradNormalizedArray = sequence_data.arrays[gradArrayName].data
                    gradAmplitude = [sequence_data.objects[gradObject].amplitude]*len(gradNormalizedArray)
                    mulitplicator = [1]*len(gradNormalizedArray)
                    if(gradArrayAmplitudeOption == "flip"): 
                        mulitplicator = [-1]*len(gradNormalizedArray)
                    elif(('type', 'equation') in list(gradArrayAmplitudeOption)): 
                        gradEquationName = dict(gradArrayAmplitudeOption)['equation']
                        gradEquationString = dict(sequence_data.equations[gradEquationName])['equation']
                        mulitplicator = [eval(gradEquationString.replace("ctr(1)", str(counter)))]*len(gradNormalizedArray)
                    else:
                        pass
                    gradArray = []
                    for gradArrayIndex in range(0, len(gradNormalizedArray)):
                        gradArray.append(mulitplicator[gradArrayIndex]*gradNormalizedArray[gradArrayIndex]*gradAmplitude[gradArrayIndex])
                    gradArrays.append(gradArray)
                    gradStartTimes.append(sequence_data.instructions[instruction].steps[stepIndex].time)
                case "rf":
                    # TO DO modulate rf pulse amplitude according to flip angle
                    rfMaxAmplitude = 10.996 # In Volts, extracted from IDEA
                    rfObject = sequence_data.instructions[instruction].steps[stepIndex].object
                    rfArrayName = sequence_data.objects[rfObject].array
                    rfArray = sequence_data.arrays[rfArrayName].data
                    rfMagnArray = []
                    rfPhaseArray = []
                    for rfIndex in range(0, len(rfArray)):
                        if rfIndex%2==0:
                            rfMagnArray.append(rfArray[rfIndex])
                        else:
                            rfPhaseArray.append(rfArray[rfIndex])
                    rfMagnArrrayWithAmplitude = list(np.array(rfMagnArray, dtype=float)*rfMaxAmplitude)
                    rfMagnArrays.append(rfMagnArrrayWithAmplitude)
                    rfPhaseArrays.append(rfPhaseArray)
                    rfStartTimes.append(sequence_data.instructions[instruction].steps[stepIndex].time)
                case "adc":
                    adcObject = sequence_data.instructions[instruction].steps[stepIndex].object
                    adcDuration = sequence_data.objects[adcObject].duration
                    adcArrays.append([1]*int(adcDuration/10))
                    adcStartTimes.append(sequence_data.instructions[instruction].steps[stepIndex].time)
                case "mark":
                    repetitionTimes.append(sequence_data.instructions[instruction].steps[stepIndex].time)
                case _: 
                    pass
    
    return [loopCounters, loopRanges, loopBlocks, repetitionTimes, gradAxis, 
            gradStartTimes, gradArrays, rfStartTimes, rfMagnArrays, 
            rfPhaseArrays, adcStartTimes, adcArrays]

def formattingTR(rawData):
    """
    Formats the raw data into separate axes and applies interpolation to achieve a 10us raster time.

    Args:
        rawData (list): The raw data to be formatted.

    Returns:
        tuple: A tuple containing the following formatted data:
            - repetitionTimes (list): The repetition times.
            - rfSampledMagnAxisTR (list): The sampled RF magnitude axis with a 10us raster time.
            - rfSampledPhaseAxisTR (list): The sampled RF phase axis with a 10us raster time.
            - zAxisTR (list): The z-axis gradients with a 10us raster time.
            - yAxisTR (list): The y-axis gradients with a 10us raster time.
            - xAxisTR (list): The x-axis gradients with a 10us raster time.
            - adcAxisTR (list): The ADC axis with a 10us raster time.
    """
    loopCounters, loopRanges, loopBlocks, repetitionTimes, gradAxis, \
    gradStartTimes, gradArrays, rfStartTimes, rfMagnArrays, \
    rfPhaseArrays, adcStartTimes, adcArrays = decodeRawData(rawData)

    ### Separating each axis and formatting the data on a 10us raster time
    xGradientsArrays = []
    yGradientsArrays = []
    zGradientsArrays = []
    xGradientStartTimes = []
    yGradientStartTimes = []
    zGradientStartTimes = []
    for gradIndex in range(0, len(gradAxis)):
        if gradAxis[gradIndex] == 'read':
            xGradientStartTimes.append(gradStartTimes[gradIndex])
            xGradientsArrays.append(gradArrays[gradIndex])
        elif gradAxis[gradIndex] == 'phase':
            yGradientStartTimes.append(gradStartTimes[gradIndex])
            yGradientsArrays.append(gradArrays[gradIndex])
        elif gradAxis[gradIndex] == 'slice':
            zGradientStartTimes.append(gradStartTimes[gradIndex])
            zGradientsArrays.append(gradArrays[gradIndex])
        else:
            print("Wrong axis name: " + str(gradAxis[gradIndex]))

    xAxisTR = [0.0]*(int(repetitionTimes[0]/10)) # Gradient raster time 10 us
    for xstartTimeIndex in range(0, len(xGradientStartTimes)):
        for modifyIndex in range(int(xGradientStartTimes[xstartTimeIndex]/10), int(xGradientStartTimes[xstartTimeIndex]/10)+len(xGradientsArrays[xstartTimeIndex])):
            xAxisTR[modifyIndex] = xGradientsArrays[xstartTimeIndex][modifyIndex - int(xGradientStartTimes[xstartTimeIndex]/10)]

    yAxisTR = [0.0]*(int(repetitionTimes[0]/10)) # Gradient raster time 10 us
    for ystartTimeIndex in range(0, len(yGradientStartTimes)):
        for modifyIndex in range(int(yGradientStartTimes[ystartTimeIndex]/10), int(yGradientStartTimes[ystartTimeIndex]/10)+len(yGradientsArrays[ystartTimeIndex])):
            yAxisTR[modifyIndex] = yGradientsArrays[ystartTimeIndex][modifyIndex - int(yGradientStartTimes[ystartTimeIndex]/10)]

    zAxisTR = [0.0]*(int(repetitionTimes[0]/10)) # Gradient raster time 10 us
    for zstartTimeIndex in range(0, len(zGradientStartTimes)):
        for modifyIndex in range(int(zGradientStartTimes[zstartTimeIndex]/10), int(zGradientStartTimes[zstartTimeIndex]/10)+len(zGradientsArrays[zstartTimeIndex])):
            zAxisTR[modifyIndex] = zGradientsArrays[zstartTimeIndex][modifyIndex - int(zGradientStartTimes[zstartTimeIndex]/10)]
    
    rfMagnAxisTR = [0.0]*(int(repetitionTimes[0]/20)) # RF raster time 20 us
    rfPhaseAxisTR = [0.0]*(int(repetitionTimes[0]/20)) # RF raster time 20 us
    for rfstartTimeIndex in range(0, len(rfStartTimes)):
        for modifyIndex in range(int(rfStartTimes[rfstartTimeIndex]/10), int(rfStartTimes[rfstartTimeIndex]/10)+len(rfMagnArrays[rfstartTimeIndex])):
            rfMagnAxisTR[modifyIndex] = rfMagnArrays[rfstartTimeIndex][modifyIndex - int(rfStartTimes[rfstartTimeIndex]/10)]
            rfPhaseAxisTR[modifyIndex] = rfPhaseArrays[rfstartTimeIndex][modifyIndex - int(rfStartTimes[rfstartTimeIndex]/10)]

    # interpolating points to go from the 20us sampled RF pulse to a 10us sampled RF pulse
    rfTimeSampling = np.arange(0, repetitionTimes[0], 20)
    rfSampledMagnAxisTR = list(np.arange(0.0, repetitionTimes[0], 10))
    rfSampledPhaseAxisTR = list(np.arange(0.0, repetitionTimes[0], 10))
    for rfSampledIndex in range(0, len(rfSampledMagnAxisTR)):
        if rfSampledIndex%2 == 0:
            rfSampledMagnAxisTR[rfSampledIndex] = rfMagnAxisTR[int(rfSampledIndex/2)]
            rfSampledPhaseAxisTR[rfSampledIndex] = rfPhaseAxisTR[int(rfSampledIndex/2)]
        else:
            rfSampledMagnAxisTR[rfSampledIndex] = np.interp(rfSampledIndex*10, rfTimeSampling, rfMagnAxisTR)
            rfSampledPhaseAxisTR[rfSampledIndex] = np.interp(rfSampledIndex*10, rfTimeSampling, rfPhaseAxisTR)

    adcAxisTR = [0.0]*(int(repetitionTimes[0]/10)) # ADC raster time 10 us
    for adcstartTimeIndex in range(0, len(adcStartTimes)):
        for modifyIndex in range(int(adcStartTimes[adcstartTimeIndex]/10), int(adcStartTimes[adcstartTimeIndex]/10)+len(adcArrays[adcstartTimeIndex])):
            adcAxisTR[modifyIndex] = adcArrays[adcstartTimeIndex][modifyIndex - int(adcStartTimes[adcstartTimeIndex]/10)]      
    return repetitionTimes, rfSampledMagnAxisTR, rfSampledPhaseAxisTR, zAxisTR, yAxisTR, xAxisTR, adcAxisTR

def plotTR(formattedTRData):
    """
    Plots the TR (repetition time) data.

    Parameters:
    - formattedTRData: The formatted TR data.

    Returns:
    None
    """
    repetitionTimes, rfSampledMagnAxisTR, rfSampledPhaseAxisTR, zAxisTR, yAxisTR, \
    xAxisTR, adcAxisTR = decodeFormattedTRData(formattedTRData)
    
    fig, axis = plt.subplots(6, 1)
    axis[0].plot(np.arange(0, repetitionTimes[0], 10), rfSampledMagnAxisTR)
    axis[0].set_xlabel('RF Magnitude')
    axis[1].plot(np.arange(0, repetitionTimes[0], 10), rfSampledPhaseAxisTR)
    axis[1].set_xlabel('RF Phase')
    axis[2].plot(np.arange(0, repetitionTimes[0], 10), zAxisTR)
    axis[2].set_xlabel('Slice Selection (z)')
    axis[3].plot(np.arange(0, repetitionTimes[0], 10), yAxisTR)
    axis[3].set_xlabel('Phase Encoding (y)')
    axis[4].plot(np.arange(0, repetitionTimes[0], 10), xAxisTR)
    axis[4].set_xlabel('Readout (x)')
    axis[5].plot(np.arange(0, repetitionTimes[0], 10), adcAxisTR)
    axis[5].set_xlabel('ADC')
    plt.show()

def generateLoopStructure(rawData):
    """
    Generates the loop structure based on the provided raw data.

    Args:
        rawData (list): The raw data to be processed.

    Returns:
        tuple: A tuple containing the sorted loop ranges and sorted loop blocks.
    """
    loopCounters, loopRanges, loopBlocks, repetitionTimes, gradAxis, \
    gradStartTimes, gradArrays, rfStartTimes, rfMagnArrays, \
    rfPhaseArrays, adcStartTimes, adcArrays = decodeRawData(rawData)

    ### Handling counters for looping
    # sorting indexes
    # sortedLoopCounters = sorted(loopCounters)
    sortedLoopRanges = [x for _, x in sorted(zip(loopCounters, loopRanges))]
    sortedLoopBlocks = [x for _, x in sorted(zip(loopCounters, loopBlocks))]
    
    return sortedLoopRanges, sortedLoopBlocks

def generateSequenceTiming(sequence_data, sortedLoopRanges, sortedLoopBlocks):
    """
    Generate sequence timing based on the given sequence data, sorted loop ranges, and sorted loop blocks.

    Args:
        sequence_data (list): The sequence data.
        sortedLoopRanges (list): The sorted loop ranges.
        sortedLoopBlocks (list): The sorted loop blocks.

    Returns:
        list: A list containing the following timing data:
            - rfMagnAxis: The RF magnitude axis.
            - rfPhaseAxis: The RF phase axis.
            - xAxis: The X axis.
            - yAxis: The Y axis.
            - zAxis: The Z axis.
            - adcAxis: The ADC axis.
            - timeAxis: The time axis.
    """
    rfMagnAxis = []
    rfPhaseAxis = []
    xAxis = []
    yAxis = []
    zAxis = []
    adcAxis = []
    timeAxis = []
    for loopIndex in range(0, len(sortedLoopRanges)):
        for counter in range(0, sortedLoopRanges[loopIndex]):
            print(sortedLoopBlocks[loopIndex] + " iteration " + str(counter))
            if(sortedLoopBlocks[loopIndex] == "block_TR"):
                ### Separating each axis and formatting the data on a 10us raster time
                rawData = extractDataFromSDL(sequence_data, counter = counter)
                formattedTRData = formattingTR(rawData)
                repetitionTimes, rfSampledMagnAxisTR, rfSampledPhaseAxisTR, zAxisTR, yAxisTR, \
                xAxisTR, adcAxisTR = decodeFormattedTRData(formattedTRData)
                rfMagnAxis += rfSampledMagnAxisTR
                rfPhaseAxis += rfSampledPhaseAxisTR
                xAxis += xAxisTR
                yAxis += yAxisTR
                zAxis += zAxisTR
                adcAxis += adcAxisTR
            elif(sortedLoopBlocks[loopIndex] == "block_phaseEncoding"):
                if(counter != 0):
                    rfMagnAxis += rfMagnAxis
                    rfPhaseAxis += rfPhaseAxis
                    xAxis += xAxis
                    yAxis += yAxis
                    zAxis += zAxis
                    adcAxis += adcAxis
                else:
                    pass
            else:
                print("Block name " + sortedLoopBlocks[loopIndex] + " not recognized.")
    
    refLength = len(xAxis)
    if(len(rfMagnAxis) == refLength and len(rfPhaseAxis) == refLength and \
       len(yAxis) == refLength and len(zAxis) == refLength and len(adcAxis) == \
       refLength):
        timeAxis = np.arange(0, refLength * 10, 10)
    else:
        print("Mismatch between axis lengths.")

    return [rfMagnAxis, rfPhaseAxis, xAxis, yAxis, zAxis, adcAxis, timeAxis]

def plotChronogram(sequenceTiming):
    """
    Plots the chronogram for the given sequence timing.

    Parameters:
    sequenceTiming (list): A list containing the sequence timing information.

    Returns:
    None
    """
    rfMagnAxis, rfPhaseAxis, xAxis, yAxis, zAxis, adcAxis, timeAxis = \
    decodeSequenceTiming(sequenceTiming)

    fig, axis = plt.subplots(6, 1)
    axis[0].plot(timeAxis, rfMagnAxis)
    axis[0].set_xlabel('RF Magnitude')
    axis[1].plot(timeAxis, rfPhaseAxis)
    axis[1].set_xlabel('RF Phase')
    axis[2].plot(timeAxis, zAxis)
    axis[2].set_xlabel('Slice Selection (z)')
    axis[3].plot(timeAxis, yAxis)
    axis[3].set_xlabel('Phase Encoding (y)')
    axis[4].plot(timeAxis, xAxis)
    axis[4].set_xlabel('Readout (x)')
    axis[5].plot(timeAxis, adcAxis)
    axis[5].set_xlabel('ADC')
    plt.show()

def convertToPsudomri(sequenceTiming):
    """
    Converts sequence timing data to Psudomri format.

    Args:
        sequenceTiming (list): List of sequence timing data.

    Returns:
        None
    """
    rfMagnAxis, rfPhaseAxis, xAxis, yAxis, zAxis, adcAxis, timeAxis = \
    decodeSequenceTiming(sequenceTiming)

    ### Header data
    totalNumberOfData = len(timeAxis) # TO DO: Is it exact?
    nbOfTransmitCoils = 1 # TO DO: Extract info from SDL?
    numberOfReceiveCoils = 1 # TO DO: Extract info from SDL?

    ### Time data
    time = timeAxis

    ### Sequence data
    receiverEvents = generateAxisHeader(adcAxis) # For now, we do not flag end of TR and crushing
    realRf = [0.0]*len(rfMagnAxis)
    imaginaryRf =  [0.0]*len(rfMagnAxis)
    for rfValueCounter in range(0, len(rfMagnAxis)):
        realRf[rfValueCounter] = rfMagnAxis[rfValueCounter]*math.cos(rfPhaseAxis[rfValueCounter])
        imaginaryRf[rfValueCounter] = rfMagnAxis[rfValueCounter]*math.sin(rfPhaseAxis[rfValueCounter])
    rfOffset = [0]*len(rfMagnAxis) # TO DO???
    # For each time step, RF should provide real, imaginary, and offset parts
    combinedRf = []
    for rfCounter in range(0, len(realRf)):
        combinedRf += [realRf[rfCounter], imaginaryRf[rfCounter], rfOffset[rfCounter]]
    # combinedRf = generateAxisHeader(combinedRf)
    xGradient = generateAxisHeader(xAxis)
    yGradient = generateAxisHeader(yAxis)
    zGradient = generateAxisHeader(zAxis)

    dataToDump = [totalNumberOfData, nbOfTransmitCoils, numberOfReceiveCoils, 
                  len(time), 1, [0.01] * len(time), 
                  receiverEvents, 
                  int(len(combinedRf)/3), 1, combinedRf, xGradient, 
                  yGradient, zGradient]
    dumpToTextFile(dataToDump)
    dumpToBinaryFile(dataToDump)

def dumpToTextFile(dataToDump):
    """
    Dump the given data to a text file.

    Args:
        dataToDump (list): The data to be dumped.

    Returns:
        None
    """
    ### Dumping in text file
    with open('Sequence.txt', 'w') as textSequenceFile:
        for data in dataToDump:
            if type(data) == int:
                textSequenceFile.write(str(data) + '\n')
            else:
                for value in data:
                   textSequenceFile.write(str(value) + '\n')

def dumpToBinaryFile(dataToDump):
    """
    Dump the given data to a binary PSudoMRI file.

    Args:
        dataToDump (list): The data to be dumped.

    Returns:
        None
    """
    ### Dumping in text file
    # stringToDump = ""
    # for data in dataToDump:
    #     if type(data) == int:
    #         stringToDump += str(pack('f', data))[2:-1]
    #         textSequenceFile.write(pack('f', data))
    #     else:
    #         for value in data:
    #             stringToDump += str(pack('f', value))[2:-1] + '\n'
    #             textSequenceFile.writepack('f', value)

    with open('Sequence.seqn', 'wb') as textSequenceFile:
        # textSequenceFile.write(stringToDump)
        for data in dataToDump:
            if type(data) == int:
                textSequenceFile.write(pack('f', data))
            else:
                for value in data:
                    textSequenceFile.write(pack('f', value))
        # for character in list(stringToDump):
            # if character != '\n':
            #     textSequenceFile.write(pack('c', character))
            # else:
            #     textSequenceFile.write('\n')      
           
      
def generateAxisHeader(axisData):
    """
    Generate the axis header data.

    Args:
        axisData (list): The list of axis data.

    Returns:
        list: The generated axis header data.
    """
    nbElementsPerLoop = len(axisData)
    nbOfLoops = 1
    fullData = [nbElementsPerLoop, nbOfLoops] + axisData

    return fullData

def listToBinary(data, fileName):
    """
    Converts a list of data to binary format and saves it to a file.

    Args:
        data (list): The list of data to be converted.
        fileName (str): The name of the file to save the binary data to.

    Returns:
        None
    """
    listToDump = np.array(data).astype('float32')
    listToDump.tofile(fileName)

def decodeRawData(rawData):
    """
    Decodes the raw data and extracts various components.

    Args:
        rawData (list): A list containing the raw data.

    Returns:
        tuple: A tuple containing the following components:
            - loopCounters (int): The loop counters.
            - loopRanges (int): The loop ranges.
            - loopBlocks (int): The loop blocks.
            - repetitionTimes (int): The repetition times.
            - gradAxis (int): The gradient axis.
            - gradStartTimes (int): The gradient start times.
            - gradArrays (int): The gradient arrays.
            - rfStartTimes (int): The RF start times.
            - rfMagnArrays (int): The RF magnitude arrays.
            - rfPhaseArrays (int): The RF phase arrays.
            - adcStartTimes (int): The ADC start times.
            - adcArrays (int): The ADC arrays.
    """
    loopCounters = rawData[0]
    loopRanges = rawData[1]
    loopBlocks = rawData[2]
    repetitionTimes = rawData[3]
    gradAxis = rawData[4]
    gradStartTimes = rawData[5]
    gradArrays = rawData[6]
    rfStartTimes = rawData[7]
    rfMagnArrays = rawData[8]
    rfPhaseArrays = rawData[9]
    adcStartTimes = rawData[10]
    adcArrays = rawData[11]

    return loopCounters, loopRanges, loopBlocks, repetitionTimes, gradAxis, \
           gradStartTimes, gradArrays, rfStartTimes, rfMagnArrays, \
           rfPhaseArrays, adcStartTimes, adcArrays

def decodeFormattedTRData(formattedTRData):
    """
    Decode the formatted TR data.

    Args:
        formattedTRData (list): A list containing the formatted TR data.

    Returns:
        tuple: A tuple containing the decoded TR data in the following order:
            - repetitionTimes (int): The repetition times.
            - rfSampledMagnAxisTR (int): The RF sampled magnitude axis TR.
            - rfSampledPhaseAxisTR (int): The RF sampled phase axis TR.
            - zAxisTR (int): The Z-axis TR.
            - yAxisTR (int): The Y-axis TR.
            - xAxisTR (int): The X-axis TR.
            - adcAxisTR (int): The ADC axis TR.
    """
    repetitionTimes = formattedTRData[0]
    rfSampledMagnAxisTR = formattedTRData[1]
    rfSampledPhaseAxisTR = formattedTRData[2]
    zAxisTR = formattedTRData[3]
    yAxisTR = formattedTRData[4]
    xAxisTR = formattedTRData[5]
    adcAxisTR = formattedTRData[6]

    return repetitionTimes, rfSampledMagnAxisTR, rfSampledPhaseAxisTR, zAxisTR, \
        yAxisTR, xAxisTR, adcAxisTR

def decodeSequenceTiming(sequenceTiming):
    """
    Decodes the sequence timing information.

    Args:
        sequenceTiming (list): A list containing the sequence timing information.

    Returns:
        tuple: A tuple containing the decoded sequence timing information in the following order:
            - rfMagnAxis (float): RF magnitude axis value.
            - rfPhaseAxis (float): RF phase axis value.
            - xAxis (float): X-axis value.
            - yAxis (float): Y-axis value.
            - zAxis (float): Z-axis value.
            - adcAxis (float): ADC axis value.
            - timeAxis (float): Time axis value.
    """
    rfMagnAxis = sequenceTiming[0]
    rfPhaseAxis = sequenceTiming[1]
    xAxis = sequenceTiming[2]
    yAxis = sequenceTiming[3]
    zAxis = sequenceTiming[4]
    adcAxis = sequenceTiming[5]
    timeAxis = sequenceTiming[6]

    return rfMagnAxis, rfPhaseAxis, xAxis, yAxis, zAxis, adcAxis, timeAxis

import struct

def binary(num):
    """
    Source: https://stackoverflow.com/questions/16444726/binary-representation-of-float-in-python-bits-not-hex
    Converts a floating-point number to its binary representation.

    Args:
        num (float): The floating-point number to convert.

    Returns:
        str: The binary representation of the input number.
    """
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))
