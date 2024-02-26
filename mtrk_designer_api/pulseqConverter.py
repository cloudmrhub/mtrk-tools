import numpy as np
import sys
import math 
import pypulseq
from types import SimpleNamespace
import matplotlib.pyplot as plt

def pulseqConverter(sequence_data):
    fillSequence(sequence_data, 
                 plot = True, 
                 write_seq = True)

def fillSequence(sequence_data, 
                 plot: bool, 
                 write_seq: bool, 
                 seq_filename: str = "sdl_pypulseq.seq"):
    # ======
    # SETUP
    # ======
    # Create a new sequence object
    seq = pypulseq.Sequence()
    Ny = sequence_data.infos.pelines 

    ## TO DO add these info to SDL
    system = pypulseq.Opts(max_grad = 28,
                           grad_unit = "mT/m",
                           max_slew = 150,
                           slew_unit = "T/m/s",
                           rf_ringdown_time = 20e-6,
                           rf_dead_time = 100e-6,
                           adc_dead_time = 10e-6)

    # ======
    # CREATE EVENTS
    # ======

    eventList = []
    timingList = []
    variableEventsList = []
    rfSpoilingList = []
    rfSpoilingFlag = False
    allVariableAmplitudesList = []
    sdlBlockName = "block_TR"

    currentBlock = sequence_data.instructions[sdlBlockName]
    for stepIndex in range(0, len(currentBlock.steps)):
        if "object" in dict(currentBlock.steps[stepIndex]):
            currentObject = sequence_data.objects[
                                           currentBlock.steps[stepIndex].object]
            if "array" in dict(currentObject):
                currentArray = sequence_data.arrays[currentObject.array]

        match currentBlock.steps[stepIndex].action:
            case "calc":
                if currentBlock.steps[stepIndex].type == "float_rfspoil":
                    rfSpoilingFlag = True 
                    rf_spoiling_inc = currentBlock.steps[stepIndex].increment   
            case "rf":
                rfSignalArray=[]
                alpha = currentObject.flipangle
                sliceThickness = currentObject.thickness*1e-3
                for value_counter in range(0, len(currentArray.data)):
                    if value_counter%2 == 0:
                        rfSignalArray.append(currentArray.data[value_counter])
                    else:
                        pass
                rfDwellTime = currentObject.duration / currentArray.size
                rfBandwidth = 2.7 / currentObject.duration*1e6
                ## TO DO verify if the bandwidth value is okay, 
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
                    rfSpoilingList.append(rfEvent) 

            case "grad":
                variableAmplitudeFlag = False
                gradientArray = []
                ## TO DO verify this conversion
                conversionmTmToHzm = 42570
                gradientAmplitude = currentObject.amplitude*conversionmTmToHzm
                if "amplitude" in dict(currentBlock.steps[stepIndex]):
                    if currentBlock.steps[stepIndex].amplitude == "flip":
                        gradientAmplitude = -gradientAmplitude
                    else: 
                        ## TO DO generalize if it is not phase
                        ## TO DO support the case of the spoiler
                        equationName = \
                            currentBlock.steps[stepIndex].amplitude.equation
                        equationString = \
                            sequence_data.equations[equationName].equation
                        equationString = equationString.replace("ctr(1)", 
                                                                "phaseStep")
                        variableAmplitudesList = []
                        for phaseStep in range(0, Ny): 
                            variableAmplitudesList.append(
                                        eval(equationString)*conversionmTmToHzm)
                        gradientAmplitude = 1
                        allVariableAmplitudesList.append(variableAmplitudesList)
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
                ## TO DO manage this delay
                adc_delay = currentBlock.steps[stepIndex].time
                adcEvent = pypulseq.make_adc(
                                        num_samples = currentObject.samples, 
                                        duration = currentObject.duration*1e-6, 
                                        delay = adc_delay*1e-6, 
                                        system = system)
                eventList.append(adcEvent)
                if rfSpoilingFlag == True:
                    rfSpoilingList.append(adcEvent)

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

    if len(rfSpoilingList) != 2:
        print("ERROR in Rf Spoiling")

    # Creating an event signature list to facilitate block sorting
    eventSignatureList = []
    eventEndTimes = []
    for eventIndex in range(0, len(eventList)):
        eventStartTime = timingList[eventIndex][0]
        eventEndTime = timingList[eventIndex][1]
        if eventList[eventIndex].type != "delay":
            eventEndTimes.append(eventEndTime)
        eventSignature = [eventIndex, eventStartTime, eventEndTime]   
        eventSignatureList.append(eventSignature)      
            
    # Sorting all events in blocks according to their overlapping
    eventIndexBlockList = []
    while eventSignatureList != []:
        signature = eventSignatureList[0]
        overlappingList = [signature[0]]
        eventSignatureList.remove(signature)
        for otherSignature in eventSignatureList:
            if signature[1] < otherSignature[2] and \
               signature[2] > otherSignature[1]:
                overlappingList.append(otherSignature[0])
        for overlappingEventIndex in overlappingList:
            for signatureFound in eventSignatureList:
                if signatureFound[0] == overlappingEventIndex:
                    eventSignatureList.remove(signatureFound)
        eventIndexBlockList.append(overlappingList)

    # # gradient spoiling
    # # TO DO !!! use these calculations for our spoilers
    # delta_k = 1 / fov
    # phase_areas = (np.arange(Ny) - Ny / 2) * delta_k
    # gx_spoil = pypulseq.make_trapezoid(channel = "x", 
    #                                    area = 2 * Nx * delta_k, 
    #                                    system = system)
    # gz_spoil = pypulseq.make_trapezoid(channel = "z", 
    #                                    area = 4 / slice_thickness, 
    #                                    system = system)

    rf_phase = 0
    rf_inc = 0

    # ======
    # CONSTRUCT SEQUENCE
    # ======
    # Loop over phase encodes and define sequence blocks
    if variableEventsList != []:
        variableAmplitudeEvent = variableEventsList[0]
        normalizedWaveform = variableAmplitudeEvent.waveform

    # Modifying delays
    ## TO DO make this more flexible, without using match/case
    elapsedDurationList = []
    for blockList in eventIndexBlockList:
        match len(blockList):
            case 1:
                elapsedDuration = pypulseq.calc_duration(
                                                        eventList[blockList[0]])
            case 2:
                elapsedDuration = pypulseq.calc_duration(
                                                        eventList[blockList[0]], 
                                                        eventList[blockList[1]])
            case 3:
                elapsedDuration = pypulseq.calc_duration(
                                                        eventList[blockList[0]], 
                                                        eventList[blockList[1]],
                                                        eventList[blockList[2]])
        elapsedDurationList.append(elapsedDuration)

    for blockListIndex in range(1, len(eventIndexBlockList)):
        for eventIndex in eventIndexBlockList[blockListIndex]:
            eventList[eventIndex].delay -= elapsedDurationList[blockListIndex-1]
            if eventList[eventIndex].delay < seq.grad_raster_time:
                eventList[eventIndex].delay = 0.0

    # Building sequence
    for i in range(Ny):
        if rfSpoilingList != []:
                ## rfSpoilingList = [rf_event, adc_event]
                rfSpoilingList[0].phase_offset = rf_phase / 180 * np.pi
                rfSpoilingList[1].phase_offset = rf_phase / 180 * np.pi
                rf_inc = divmod(rf_inc + rf_spoiling_inc, 360.0)[1]
                rf_phase = divmod(rf_phase + rf_inc, 360.0)[1]
        ## TO DO make this more flexible, without using match/case
        for blockList in eventIndexBlockList:
            if variableEventsList != []:
                for variableAmplitudeEventIndex in range(0, 
                                                       len(variableEventsList)):
                    variableAmplitudeEvent = \
                       variableEventsList[variableAmplitudeEventIndex]
                    amplitude = \
                       allVariableAmplitudesList[variableAmplitudeEventIndex][i]
                    variableAmplitudeEvent.waveform = \
                       amplitude*(normalizedWaveform)
            match len(blockList):
                case 1:
                    seq.add_block(eventList[blockList[0]])
                case 2:
                    seq.add_block(eventList[blockList[0]], 
                                  eventList[blockList[1]])
                case 3:
                    seq.add_block(eventList[blockList[0]], 
                                  eventList[blockList[1]], 
                                  eventList[blockList[2]])
    
    # Check whether the timing of the sequence is correct
    ok, error_report = seq.check_timing()
    if ok:
        print("Timing check passed successfully")
    else:
        print("Timing check failed. Error listing follows:")
        [print(e) for e in error_report]


    # # ======
    # VISUALIZATION
    # ======
    if plot:
        seq.plot()

    seq.calculate_kspace()

    # Very optional slow step, but useful for testing during development e.g. 
    # for the real TE, TR or for staying within
    # slew-rate limits
    # rep = seq.test_report()
    # print(rep)

    # =========
    # WRITE .SEQ
    # =========
    slice_thickness = sequence_data.objects["rf_excitation"].thickness*1e-3
    fov = sequence_data.infos.fov*1e-3  # Define FOV and resolution
    if write_seq:
        # Prepare the sequence output for the scanner
        seq.set_definition(key="FOV", value=[fov, fov, slice_thickness])
        seq.set_definition(key="Name", value=sequence_data.infos.seqstring)

        seq.write(seq_filename)
