import numpy as np
import sys
import math 
import pypulseq
from types import SimpleNamespace
import matplotlib.pyplot as plt

def pulseqConverter(sequence_data):
    fillSequence(sequence_data, plot=True, write_seq=True)

def fillSequence(sequence_data, plot: bool, write_seq: bool, seq_filename: str = "sdl_pypulseq.seq"):
    # ======
    # SETUP
    # ======
    # Create a new sequence object
    seq = pypulseq.Sequence()
    fov = sequence_data.infos.fov*1e-3  # Define FOV and resolution
    Nx = sequence_data.objects["adc_readout"].samples
    Ny = sequence_data.infos.pelines
    slice_thickness = sequence_data.objects["rf_excitation"].thickness*1e-3  # slice

    # for step in sequence_data.instructions["block_TR"].steps:
    #     if step.action == "calc" and step.type == "float_rfspoil":
    #         increment = step.increment
    # rf_spoiling_inc = increment  # RF spoiling increment

    # !!! TO DO add these info to SDL
    system = pypulseq.Opts(
        max_grad=28,
        grad_unit="mT/m",
        max_slew=150,
        slew_unit="T/m/s",
        rf_ringdown_time=20e-6,
        rf_dead_time=100e-6,
        adc_dead_time=10e-6,
        
    )

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
    for stepIndex in range(0, len(sequence_data.instructions[sdlBlockName].steps)):
        if "object" in dict(sequence_data.instructions[sdlBlockName].steps[stepIndex]):
            currentObject = sequence_data.instructions[sdlBlockName].steps[stepIndex].object
        match sequence_data.instructions[sdlBlockName].steps[stepIndex].action:
            case "calc":
                if sequence_data.instructions[sdlBlockName].steps[stepIndex].type == "float_rfspoil":
                    rfSpoilingFlag = True 
                    rf_spoiling_inc =  sequence_data.instructions[sdlBlockName].steps[stepIndex].increment   
            case "rf":
                rfSignalArray=[]
                alpha = sequence_data.objects[currentObject].flipangle  # flip angle
                sliceThickness = sequence_data.objects[currentObject].thickness*1e-3  # slice
                for value_counter in range(0, len(sequence_data.arrays[sequence_data.objects[currentObject].array].data)):
                    if value_counter%2 == 0:
                        rfSignalArray.append(sequence_data.arrays[sequence_data.objects[currentObject].array].data[value_counter])
                    else:
                        pass
                rfDwellTime = sequence_data.objects[currentObject].duration/sequence_data.arrays[sequence_data.objects[currentObject].array].size
                rfBandwidth = 2.7/sequence_data.objects[currentObject].duration*1e6
                rfEvent = pypulseq.make_arbitrary_rf(
                    signal=np.array(rfSignalArray),
                    flip_angle=alpha * math.pi / 180,
                    bandwidth=rfBandwidth, # !!! TO DO verify is this value is okay, see if BW*time=2.7
                    delay=sequence_data.instructions[sdlBlockName].steps[stepIndex].time*1e-6,
                    dwell=rfDwellTime*1e-6, 
                    freq_offset=0,
                    no_signal_scaling=False,
                    max_grad=0,
                    max_slew=0,
                    phase_offset=0,
                    return_delay=False,
                    return_gz=False,
                    slice_thickness=sliceThickness,
                    system=system,
                    time_bw_product=2.7,
                    use=sequence_data.objects[currentObject].purpose)
                eventList.append(rfEvent)
                if rfSpoilingFlag == True and sequence_data.objects[currentObject].purpose == "excitation":
                    rfSpoilingList.append(rfEvent)  
            case "grad":
                variableAmplitudeFlag = False
                gradientArray = []
                conversionmTmToHzm = 42570 #!!! To do verify this conversion
                gradientAmplitude = sequence_data.objects[currentObject].amplitude*conversionmTmToHzm
                if "amplitude" in dict(sequence_data.instructions[sdlBlockName].steps[stepIndex]):
                    if sequence_data.instructions[sdlBlockName].steps[stepIndex].amplitude == "flip":
                        gradientAmplitude = -gradientAmplitude
                    else: 
                        # TO DO generalize if it is not phase
                        # TO DO support the case of the spoiler
                        equationName = sequence_data.instructions[sdlBlockName].steps[stepIndex].amplitude.equation
                        equationString = sequence_data.equations[equationName].equation
                        equationString = equationString.replace("ctr(1)", "phaseStep")
                        variableAmplitudesList = []
                        for phaseStep in range(0, Ny): 
                            variableAmplitudesList.append(eval(equationString)*conversionmTmToHzm)
                        # gradientAmplitude = variableAmplitudesList[0]
                        gradientAmplitude = 1
                        allVariableAmplitudesList.append(variableAmplitudesList)
                        variableAmplitudeFlag = True

                for value in sequence_data.arrays[sequence_data.objects[currentObject].array].data:
                    gradientArray.append(gradientAmplitude * value)
                gradientAxis = ""
                if sequence_data.instructions[sdlBlockName].steps[stepIndex].axis == "slice":
                    gradientAxis = 'z'
                elif sequence_data.instructions[sdlBlockName].steps[stepIndex].axis == "read":
                    gradientAxis = 'x'
                elif sequence_data.instructions[sdlBlockName].steps[stepIndex].axis == "phase":
                    gradientAxis = 'y'
                else:
                    print(str(sequence_data.instructions[sdlBlockName].steps[stepIndex].axis) + "is not a valid axis name.")
                gradientEvent = pypulseq.make_arbitrary_grad(
                    channel=gradientAxis,
                    waveform=np.array(gradientArray),
                    delay=sequence_data.instructions[sdlBlockName].steps[stepIndex].time*1e-6,
                    system=system)
                eventList.append(gradientEvent)
                if variableAmplitudeFlag == True:
                    variableEventsList.append(gradientEvent)

            case "adc":
                # adc_delay = sequence_data.objects["grad_read_readout"].duration - sequence_data.objects["adc_readout"].duration
                adc_delay = sequence_data.instructions[sdlBlockName].steps[stepIndex].time # !!! TO DO manage this delay
                adcEvent = pypulseq.make_adc(num_samples = Nx, 
                                             duration = sequence_data.objects[currentObject].duration*1e-6, 
                                             delay = adc_delay*1e-6, 
                                             system = system)
                eventList.append(adcEvent)
                if rfSpoilingFlag == True:
                    rfSpoilingList.append(adcEvent)  
            case "mark":
                eventList.append(pypulseq.make_delay(sequence_data.instructions[sdlBlockName].steps[stepIndex].time*1e-6))
        if "object" in dict(sequence_data.instructions[sdlBlockName].steps[stepIndex]) or\
            sequence_data.instructions[sdlBlockName].steps[stepIndex].action == "mark":
            if sequence_data.instructions[sdlBlockName].steps[stepIndex].action == "sync":
                pass
            elif sequence_data.instructions[sdlBlockName].steps[stepIndex].action == "mark": 
                startTime = sequence_data.instructions[sdlBlockName].steps[stepIndex].time
                endTime = sequence_data.instructions[sdlBlockName].steps[stepIndex].time
                timingList.append([startTime, endTime])  
            else:
                startTime = sequence_data.instructions[sdlBlockName].steps[stepIndex].time
                endTime = startTime + sequence_data.objects[currentObject].duration
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
    
    # for eventIndex in range(0,len(eventList)):
    #     # !!! TO DO generalize (only going for one TR here)
    #     if eventList[eventIndex].type == "delay":
    #         lastEventEndTime = eventEndTimes[eventEndTimes.index(max(eventEndTimes))]
    #         eventEndTime = eventSignatureList[eventIndex][2]
    #         delayDuration = np.ceil(((eventEndTime-lastEventEndTime)*1e-6)/ seq.grad_raster_time)* seq.grad_raster_time
    #         eventList[eventIndex] = pypulseq.make_delay(delayDuration)
            

    # Sorting all events in blocks according to their overlapping
    eventIndexBlockList = []
    while eventSignatureList != []:
        signature = eventSignatureList[0]
        overlappingList = [signature[0]]
        eventSignatureList.remove(signature)
        for otherSignature in eventSignatureList:
            if signature[1]<otherSignature[2] and signature[2]>otherSignature[1]:
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
    # gx_spoil = pypulseq.make_trapezoid(channel="x", area=2 * Nx * delta_k, system=system)
    # gz_spoil = pypulseq.make_trapezoid(channel="z", area=4 / slice_thickness, system=system)

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
    elapsedDurationList = []
    for blockList in eventIndexBlockList:
        match len(blockList):
            case 1:
                elapsedDuration = pypulseq.calc_duration(eventList[blockList[0]])
            case 2:
                elapsedDuration = pypulseq.calc_duration(eventList[blockList[0]], 
                                                         eventList[blockList[1]])
            case 3:
                elapsedDuration = pypulseq.calc_duration(eventList[blockList[0]], 
                                                            eventList[blockList[1]],
                                                            eventList[blockList[2]])
        elapsedDurationList.append(elapsedDuration)

    print("+-+-+ seq.grad_raster_time " + str(seq.grad_raster_time))
    for blockListIndex in range(1, len(eventIndexBlockList)):
        for eventIndex in eventIndexBlockList[blockListIndex]:
            eventList[eventIndex].delay -= elapsedDurationList[blockListIndex-1]
            if eventList[eventIndex].delay < seq.grad_raster_time:
                eventList[eventIndex].delay = 0.0

    # Building sequence
    for i in range(Ny):
        if rfSpoilingList != []:
                # rfSpoilingList = [rf_event, adc_event]
                rfSpoilingList[0].phase_offset = rf_phase / 180 * np.pi
                rfSpoilingList[1].phase_offset = rf_phase / 180 * np.pi
                rf_inc = divmod(rf_inc + rf_spoiling_inc, 360.0)[1]
                rf_phase = divmod(rf_phase + rf_inc, 360.0)[1]
        # TD DO make this more flexible, without using match/case
        for blockList in eventIndexBlockList:
            if variableEventsList != []:
                for variableAmplitudeEventIndex in range(0, len(variableEventsList)):
                    variableAmplitudeEvent = variableEventsList[variableAmplitudeEventIndex]
                    amplitude = allVariableAmplitudesList[variableAmplitudeEventIndex][i]
                    variableAmplitudeEvent.waveform = amplitude*(normalizedWaveform)
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

    # Very optional slow step, but useful for testing during development e.g. for the real TE, TR or for staying within
    # slew-rate limits
    # rep = seq.test_report()
    # print(rep)

    # =========
    # WRITE .SEQ
    # =========
    if write_seq:
        # Prepare the sequence output for the scanner
        seq.set_definition(key="FOV", value=[fov, fov, slice_thickness])
        seq.set_definition(key="Name", value=sequence_data.infos.seqstring)

        seq.write(seq_filename)
