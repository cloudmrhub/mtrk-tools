################################################################################
### mtrk project - Pypulseq-based conversion tool from SDL to Pulseq.        ###
### Version 0.1.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 04/29/2024              ###
################################################################################

import numpy as np
import sys
import math 
import pypulseq
from types import SimpleNamespace
import matplotlib.pyplot as plt

def pulseqConverter(sequence_data):
    """
    Converts the given sequence data to a Pulseq format.

    Args:
        sequence_data (dict): The sequence data to be converted.

    Returns:
        None
    """
    fillSequence(sequence_data, 
                 plot=True, 
                 write_seq=True)

def fillSequence(sequence_data, 
                 plot: bool, 
                 write_seq: bool, 
                 seq_filename: str = "sdl_pypulseq.seq"):
    """
    Fills the sequence object with instructions and parameters based on the given sequence data.

    Args:
        sequence_data: The sequence data containing instructions and parameters.
        plot: A boolean indicating whether to plot the sequence.
        write_seq: A boolean indicating whether to write the sequence in Pulseq .seq format.
        seq_filename: The filename to use when writing the sequence in Pulseq .seq format.

    Returns:
        None
    """

    ############################################################################
    ## Creating new sequence object and system specifications
    ############################################################################

    seq = pypulseq.Sequence()

    ## TO DO add these info to SDL
    system = pypulseq.Opts(max_grad = 28,
                           grad_unit = "mT/m",
                           max_slew = 150,
                           slew_unit = "T/m/s",
                           rf_ringdown_time = 20e-6,
                           rf_dead_time = 100e-6,
                           adc_dead_time = 10e-6)

    ############################################################################
    ## Creating sequence structure from the SDL file
    ############################################################################

    loopCountersList = []
    mainBlock = sequence_data.instructions["main"]
    stepInfoList = extractStepInformation(
                                        sequence_data = sequence_data, 
                                        currentBlock = mainBlock, 
                                        system = system,
                                        loopCountersList = loopCountersList,
                                        seq = seq)

    counterRangeList, stepInfoList = extractSequenceStructure( 
                                        sequence_data = sequence_data, 
                                        stepInfoList = stepInfoList, 
                                        system = system, 
                                        loopCountersList = loopCountersList, 
                                        seq = seq, 
                                        counterRange = 0, 
                                        blockName = "main", 
                                        counterRangeList = [])

    actionList = organizePulseqBlocks(sequence_data = sequence_data, 
                                      counterRangeList = counterRangeList, 
                                      system = system, 
                                      seq = seq, 
                                      loopCountersList = loopCountersList)
 
    buildPulseqSequence(seq = seq,
                        actionIndex = 0, 
                        actionList = actionList, 
                        stepInfoList = stepInfoList)

    ############################################################################
    ## Checking timing
    ############################################################################

    ok, error_report = seq.check_timing()
    if ok:
        print("Timing check passed successfully")
    else:
        print("Timing check failed. Error listing follows:")
        [print(e) for e in error_report]

    ############################################################################
    ## Plotting and reporting
    ############################################################################
    if plot:
        seq.plot()

    seq.calculate_kspace()

    # Very optional slow step, but useful for testing during development e.g. 
    # for the real TE, TR or for staying within slew-rate limits
    # rep = seq.test_report()
    # print(rep)

    ############################################################################
    ## Writitng the sequence in Pulseq .seq format
    ############################################################################

    slice_thickness = sequence_data.objects["rf_excitation"].thickness*1e-3
    fov = sequence_data.infos.fov*1e-3
    print("Raster time check: ", seq.rfRasterTime)
    if write_seq:
        # Prepare the sequence output for the scanner
        seq.set_definition(key="FOV", value=[fov, fov, slice_thickness])
        seq.set_definition(key="Name", value=sequence_data.infos.seqstring)
        # seq.set_definition(key="RadiofrequencyRasterTime", value=seq.rfRasterTime)
        # seq.set_definition(key="GradientRasterTime", value=1e-5)

        seq.write(seq_filename)

################################################################################
## Functions to convert from SDL to Pulseq
################################################################################

def extractStepInformation(sequence_data, currentBlock, system, 
                           loopCountersList, seq):
    """
    Extracts step information from the given sequence data and current block.

    Args:
        sequence_data (SequenceData): The sequence data object containing the sequence information.
        currentBlock (Block): The current block object.
        system (System): The system object representing the MRI system.
        loopCountersList (list): The list of loop counters.
        seq (Sequence): The sequence object.

    Returns:
        list: A list containing the extracted step information, including event list, RF spoiling list,
              equations list, variable events list, RF spoiling increment, and event index block list.
    """
    eventList = []
    rfSpoilingList = []
    allEquationsList = []
    variableEventsList = []
    timingList = []
    rfSpoilingInc = 0
    rfSpoilingFlag = False
    for stepIndex in range(0, len(currentBlock.steps)):
        if "object" in dict(currentBlock.steps[stepIndex]):
            currentObject = sequence_data.objects[
                                           currentBlock.steps[stepIndex].object]
            if "array" in dict(currentObject):
                currentArray = sequence_data.arrays[currentObject.array]
        match currentBlock.steps[stepIndex].action:

            case "loop":
                loopCounter = currentBlock.steps[stepIndex].counter
                loopRange = currentBlock.steps[stepIndex].range
                loopStepInfoList = \
                        extractStepInformation(
                                   sequence_data = sequence_data, 
                                   currentBlock = currentBlock.steps[stepIndex], 
                                   system = system,
                                   loopCountersList = loopCountersList,
                                   seq = seq)
                loopEvent = ["loop", loopCounter, loopRange, loopStepInfoList]
                eventList.append(loopEvent)

            case "run_block":
                blockToRun = str(currentBlock.steps[stepIndex].block)
                eventList.append(["run_block", blockToRun])

            case "calc":
                if currentBlock.steps[stepIndex].type == "float_rfspoil":
                    rfSpoilingFlag = True 
                    rfSpoilingInc = currentBlock.steps[stepIndex].increment 

            case "rf":
                rfSignalArray=[]
                alpha = currentObject.flipangle
                sliceThickness = currentObject.thickness*1e-3
                for value_counter in range(0, len(currentArray.data)):
                    if value_counter%2 == 0:
                        rfSignalArray.append(currentArray.data[value_counter])
                    else:
                        pass
                rasterTime = int(currentObject.duration / (10*currentArray.size) )
                seq.rfRasterTime = 1e-5 * rasterTime
                rfDwellTime = currentObject.duration / currentArray.size
                rfBandwidth = 2.7 / currentObject.duration*1e6
                ## TO DO verify the bandwidth value
                rfEvent = pypulseq.make_arbitrary_rf(
                                signal = np.array(rfSignalArray),
                                flip_angle = alpha * math.pi / 180,
                                bandwidth = rfBandwidth, 
                                delay = currentBlock.steps[stepIndex].time*1e-6,
                                dwell = rfDwellTime*1e-6, 
                                freq_offset = 0,
                                no_signal_scaling = False,
                                max_grad = 0,
                                max_slew = 0,
                                phase_offset = 0,
                                return_delay = False,
                                return_gz = False,
                                slice_thickness = sliceThickness,
                                system = system,
                                time_bw_product = 2.7,
                                use = currentObject.purpose)
                eventList.append(rfEvent)
                if rfSpoilingFlag == True and \
                   currentObject.purpose == "excitation":
                    rfSpoilingList.append(eventList.index(rfEvent))

            case "grad":
                variableAmplitudeFlag = False
                gradientArray = []
                gyromagneticRatio = 42.577*1e6 # Hz/T converting mT/m to Hz/m
                gradientAmplitude = currentObject.amplitude*gyromagneticRatio*1e-3
                if "amplitude" in dict(currentBlock.steps[stepIndex]):
                    if currentBlock.steps[stepIndex].amplitude == "flip":
                        gradientAmplitude = -gradientAmplitude
                    else: 
                        equationName = \
                            currentBlock.steps[stepIndex].amplitude.equation
                        equationString = \
                            sequence_data.equations[equationName].equation                      
                        gradientAmplitude = 1
                        allEquationsList.append(equationString)
                        variableAmplitudeFlag = True
                for value in currentArray.data:
                    gradientArray.append(gradientAmplitude * value)
                gradientAxis = ""
                if currentBlock.steps[stepIndex].axis == "slice":
                    gradientAxis = 'z'
                elif currentBlock.steps[stepIndex].axis == "read":
                    gradientAxis = 'x'
                elif currentBlock.steps[stepIndex].axis == "phase":
                    gradientAxis = 'y'
                else:
                    print(str(currentBlock.steps[stepIndex].axis) + \
                          "is not a valid axis name.")
                gradientEvent = pypulseq.make_arbitrary_grad(
                                channel = gradientAxis,
                                waveform = np.array(gradientArray),
                                delay = currentBlock.steps[stepIndex].time*1e-6,
                                system = system)
                eventList.append(gradientEvent)
                if variableAmplitudeFlag == True:
                    variableEventsList.append(gradientEvent)

            case "adc":
                adc_delay = currentBlock.steps[stepIndex].time
                adcEvent = pypulseq.make_adc(
                                        num_samples = currentObject.samples, 
                                        duration = currentObject.duration*1e-6, 
                                        delay = adc_delay*1e-6, 
                                        system = system)
                eventList.append(adcEvent)
                if rfSpoilingFlag == True:
                    rfSpoilingList.append(eventList.index(adcEvent))
            case "mark":
                eventList.append(pypulseq.make_delay(
                                       currentBlock.steps[stepIndex].time*1e-6))
                
        if "object" in dict(currentBlock.steps[stepIndex]) or\
            currentBlock.steps[stepIndex].action == "mark":
            if currentBlock.steps[stepIndex].action == "sync":
                pass
            elif currentBlock.steps[stepIndex].action == "mark": 
                startTime = currentBlock.steps[stepIndex].time
                endTime = currentBlock.steps[stepIndex].time
                timingList.append([startTime, endTime])  
            else:
                startTime = currentBlock.steps[stepIndex].time
                endTime = startTime + currentObject.duration
                timingList.append([startTime, endTime])

    if len(rfSpoilingList) != 2 and len(rfSpoilingList) != 0:
        ## TO DO see if there can be other cases
        print("ERROR in Rf Spoiling")

    ## Creating an event signature list to facilitate block sorting
    eventSignatureList = []
    eventEndTimes = []
    for eventIndex in range(0, len(eventList)):
        if type(eventList[eventIndex]) != list:
            eventStartTime = timingList[eventIndex][0]
            eventEndTime = timingList[eventIndex][1]
            if eventList[eventIndex].type != "delay":
                eventEndTimes.append(eventEndTime)
            eventSignature = [eventIndex, eventStartTime, eventEndTime]   
            eventSignatureList.append(eventSignature)     
    eventSignatureList = sorted(eventSignatureList, key=lambda x: x[1])

    ## Sorting all events in blocks according to their overlapping
    eventIndexBlockList = []
    while eventSignatureList != []:
        signature = eventSignatureList[0]
        overlappingList = [signature[0]]
        eventSignatureList.remove(signature)
        for otherSignature in eventSignatureList:
            if signature[1] <= otherSignature[2] and \
               signature[2] > otherSignature[1]:
                overlappingList.append(otherSignature[0])
        for overlappingEventIndex in overlappingList:
            for signatureFound in eventSignatureList:
                if signatureFound[0] == overlappingEventIndex:
                    eventSignatureList.remove(signatureFound)
        eventIndexBlockList.append(overlappingList)


    ## Modifying delays
    elapsedDurationList = []
    for blockList in eventIndexBlockList:
        listToAdd = []
        for blockIndex in range(0, len(blockList)):
            listToAdd.append(eventList[blockList[blockIndex]])
        elapsedDuration = pypulseq.calc_duration(*listToAdd)
        elapsedDurationList.append(elapsedDuration)
    for blockListIndex in range(1, len(eventIndexBlockList)):
        for eventIndex in eventIndexBlockList[blockListIndex]:
            eventList[eventIndex].delay -= \
                                       elapsedDurationList[blockListIndex-1]
            if eventList[eventIndex].delay < seq.grad_raster_time:
                eventList[eventIndex].delay = 0.0

    stepInfoList =  [eventList, rfSpoilingList, 
                     allEquationsList, variableEventsList, 
                     rfSpoilingInc, eventIndexBlockList]
    return stepInfoList

def buildPulseqSequenceBlocks(index, seq, stepInfoList, normalizedWaveform, 
                              rf_inc, rf_phase):
    """
    Builds Pulseq sequence blocks based on the given parameters.

    Args:
        index (int): The index of the sequence block.
        seq (PulseqSequence): The Pulseq sequence object.
        stepInfoList (list): A list containing various step information.
        normalizedWaveform (ndarray): The normalized waveform.
        rf_inc (float): The RF increment.
        rf_phase (float): The RF phase.

    Returns:
        tuple: A tuple containing the updated stepInfoList, rf_inc, and rf_phase.
    """
    ## stepInfoList =  [eventList, rfSpoilingList, 
    ##                  allEquationsList, variableEventsList, 
    ##                  rfSpoilingInc, eventIndexBlockList]
    for blockList in stepInfoList[5]:
        if stepInfoList[3] != []:
            for variableAmplitudeEventIndex in range(0, len(stepInfoList[3])):
                equationString = stepInfoList[2][variableAmplitudeEventIndex]
                counterNumberFound = False
                stringCounterIndex = 0
                while counterNumberFound == False:
                    if "ctr(" + str(stringCounterIndex) + ")" in \
                                                                 equationString:
                        stringToReplace = \
                                     str("ctr(" + str(stringCounterIndex) + ")")
                        counterNumberFound = True
                    stringCounterIndex += 1
                equationString = equationString.replace(stringToReplace,
                                                        "index")
                variableAmplitudeEvent = \
                   stepInfoList[3][variableAmplitudeEventIndex]
                gyromagneticRatio = 42577 # Hz/T converting mT/m to Hz/m
                amplitude = eval(equationString)*gyromagneticRatio
                variableAmplitudeEvent.waveform = amplitude*(normalizedWaveform)
        listToAdd = []
        for blockIndex in range(0, len(blockList)):
            if stepInfoList[0][blockList[blockIndex]].type == "rf" and \
                stepInfoList[0][blockList[blockIndex]].use == "excitation":
                rf_inc += stepInfoList[4]
                rf_phase += rf_inc
                rf_phase = divmod(rf_phase, 360.0)[1]
                rf_inc = divmod(rf_inc, 360.0)[1]
                stepInfoList[0][blockList[blockIndex]].phase_offset = \
                                                        rf_phase / 180 * np.pi
            elif stepInfoList[0][blockList[blockIndex]].type == "rf" and \
                stepInfoList[0][blockList[blockIndex]].use == "refocusing":
                stepInfoList[0][blockList[blockIndex]].phase_offset = \
                                                       rf_phase / 180 * np.pi
            elif stepInfoList[0][blockList[blockIndex]].type == "adc":
                stepInfoList[0][blockList[blockIndex]].phase_offset = \
                                                       rf_phase / 180 * np.pi
            listToAdd.append(stepInfoList[0][blockList[blockIndex]])
        seq.add_block(*listToAdd)
    return stepInfoList, rf_inc, rf_phase
                    
def extractSequenceStructure(sequence_data, stepInfoList, system, 
                             loopCountersList, seq, counterRange, blockName, 
                             counterRangeList):
    """
    Extracts the sequence structure by recursively traversing the stepInfoList.

    Args:
        sequence_data (SequenceData): The sequence data object.
        stepInfoList (list): The list of step information.
        system (System): The system object.
        loopCountersList (list): The list of loop counters.
        seq (Sequence): The sequence object.
        counterRange (int): The counter range.
        blockName (str): The name of the block.
        counterRangeList (list): The list of counter ranges.

    Returns:
        tuple: A tuple containing the counterRangeList and stepInfoList.
    """
    for event in stepInfoList[0]:
        if type(event) == list and event[0] == "loop":
            counterId = event[1]
            counterRange = event[2]
            for loopEvent in event[3][0]:
                if type(loopEvent) == list and loopEvent[0] == "run_block":
                    blockName = loopEvent[1]
                    blockStepInfoList = extractStepInformation(
                       sequence_data = sequence_data, 
                       currentBlock = sequence_data.instructions[blockName], 
                       system = system,
                       loopCountersList = loopCountersList,
                       seq = seq)
                    counterRangeList.append([counterId, counterRange, blockName])
                    counterRangeList, stepInfoList = \
                        extractSequenceStructure(
                                          sequence_data = sequence_data, 
                                          stepInfoList = blockStepInfoList, 
                                          system = system, 
                                          loopCountersList = loopCountersList, 
                                          seq = seq, 
                                          counterRange = counterRange, 
                                          blockName = blockName, 
                                          counterRangeList = counterRangeList)
    return counterRangeList, stepInfoList

def organizePulseqBlocks(sequence_data, counterRangeList, system, seq, 
                         loopCountersList):
    """
    Organizes the Pulseq blocks based on the given sequence data, counter range list,
    system, sequence, and loop counters list.

    Args:
        sequence_data (SequenceData): The sequence data containing instructions.
        counterRangeList (list): A list of counter ranges.
        system (System): The system information.
        seq (Sequence): The sequence information.
        loopCountersList (list): A list of loop counters.

    Returns:
        list: A list of action lists containing the counters, block step information,
              and normalized waveform.

    """
    actionList = []
    for counter in counterRangeList:
        if sequence_data.instructions[counter[2]].steps[0].action == "loop":
            actionList.append([counter])
        else: 
            blockStepInfoList = extractStepInformation(
                   sequence_data = sequence_data, 
                   currentBlock = sequence_data.instructions[counter[2]], 
                   system = system,
                   loopCountersList = loopCountersList,
                   seq = seq)
            if blockStepInfoList[3] != []:
                variableAmplitudeEvent = blockStepInfoList[3][0]
                normalizedWaveform = variableAmplitudeEvent.waveform
            actionList.append([counter, blockStepInfoList, normalizedWaveform])
    return actionList

def buildPulseqSequence(seq, actionIndex, actionList, stepInfoList):
    """
    Builds a Pulseq sequence based on the given parameters.

    Args:
        seq (object): The Pulseq sequence object.
        actionIndex (int): The index of the current action in the actionList.
        actionList (list): The list of actions to be performed.
        stepInfoList (list): The list of step information.

    Returns:
        None
    """
    if len(actionList[actionIndex]) != 1:
        rf_phase = 0
        rf_inc = 0
        for index in range(0, actionList[actionIndex][0][1]):
            stepInfoList, rf_inc, rf_phase = buildPulseqSequenceBlocks(
                index = index, 
                seq = seq, 
                stepInfoList = actionList[actionIndex][1], 
                normalizedWaveform = actionList[actionIndex][2], 
                rf_inc = rf_inc, 
                rf_phase = rf_phase)
    else:
        for index in range(0, actionList[actionIndex][0][1]):
            buildPulseqSequence(seq = seq, 
                                actionIndex = actionIndex + 1, 
                                actionList = actionList, 
                                stepInfoList = stepInfoList)
            
            