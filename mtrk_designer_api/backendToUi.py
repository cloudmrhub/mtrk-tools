################################################################################
### mtrk project - Transition from backend to UI.                            ###
### Version 0.0.0                                                            ###
### Anais Artiges and the mtrk project team at NYU - 04/29/2024              ###
################################################################################  

import json
import jsbeautifier
import re
import ast
from pprint import pprint
from numpy import add
from sdlFileCreator import *

#############################################################
### Creating SDL file from web-based UI
#############################################################

def create_sdl_from_ui_inputs(block_to_box_objects, block_structure, 
                              block_to_loops, block_to_duration, 
                              block_number_to_block_object, configurations):
    ### Initialize SDL file
    ## TO DO - need to intialize without loading file
    with open('init_data/miniflash.mtrk') as sdlFile:
        sdlData = json.load(sdlFile)
        sequence_data = PulseSequence(**sdlData)
    sdlInitialize(sequence_data)

    updateSDLFile(sequence_data, block_to_box_objects, configurations,
                  block_number_to_block_object, block_to_loops, 
                  block_to_duration)
    
    ### writing of json schema to SDL file with formatting options
    with open('output.mtrk', 'w') as sdlFileOut:
        options = jsbeautifier.default_options()
        options.indent_size = 4
        data_to_print = jsbeautifier.beautify(\
                     json.dumps(sequence_data.model_dump(mode="json")), options)
        sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) 
        #purely aesthetic

def updateSDLFile(sequence_data, boxes, configurations, 
                  block_number_to_block_object, block_to_loops, 
                  block_to_duration):
    keys = boxes.keys()
    for boxKey in keys:
        boxList = boxes[boxKey]
        for box in boxList:
            ## TO DO intervert the values
            if box["type"] == "event":
                box["type"] = box["axis"]
                box["axis"] = "event"
            if box["type"] == "Block":
                box["type"] = "loop"
                box["name"] = \
                         block_number_to_block_object[str(box["block"])]["name"]
                box["loop_number"] = block_to_loops[box["name"]]
                if {"type": "mark", "start_time": box["start_time"] + \
                      block_to_duration[box["name"]]*1e3} in boxes[box["name"]]:
                    pass
                else:
                    boxes[box["name"]].append({"type": "mark", "start_time": \
                                            box["start_time"] + \
                                            block_to_duration[box["name"]]*1e3})
                    boxes[box["name"]].append({"type": "submit"})
            if boxKey == "Main":
                instructionName = "main"
                instructionHeader = ["Main loop", "on"]
                ## TO DO put this information in the right place
                print("+-+-+ testou " + str(bool(block_number_to_block_object)))
                savedInstructionHeader = []
                if bool(block_number_to_block_object):
                    if block_number_to_block_object[str(box["block"])][\
                                                       "print_counter"] == True:
                        printCounter = "on"
                    else:
                        printCounter = "off"
                    savedInstructionHeader = \
                    [block_number_to_block_object[str(box["block"])]["message"],
                                                                   printCounter]
            else:
                instructionName = boxKey
                instructionHeader = savedInstructionHeader
                
                
        
        addInstruction(sequence_data, instructionName)
        instructionInformationList = getInstructionInformation(
                                        boxes = boxList,
                                        instructionName = instructionName,
                                        instructionHeader = instructionHeader)
        completeInstructionInformation(
                        sequence_data = sequence_data, 
                        instructionInformationList = instructionInformationList)
    fileInformationList = getFileInformation(configurations = configurations)
    completeFileInformation(sequence_data = sequence_data, 
                            fileInformationList = fileInformationList)
    settingsInformationList = getSequenceSettingsInformation(
                                                configurations = configurations)
    completeSequenceSettings(sequence_data = sequence_data, 
                             settingsInformationList = settingsInformationList)
    sequenceInfoInformationList = getSequenceInfoInformation(
                                                configurations = configurations)
    completeSequenceInformation(
                      sequence_data = sequence_data, 
                      sequenceInfoInformationList = sequenceInfoInformationList)

        
#############################################################
### Functions to get new values from the web-based UI
#############################################################

def getFileInformation(configurations):
    formatInfo = configurations["file"]["format"]
    versionInfo = configurations["file"]["version"]
    measurementInfo = configurations["file"]["measurement"]
    systemInfo = configurations["file"]["system"]
    fileInformationList = [formatInfo, versionInfo, measurementInfo, 
                           systemInfo]
    return fileInformationList

def getSequenceSettingsInformation(configurations):
    readoutOsInfo = configurations["settings"]["readout"]
    settingsInformationList = [readoutOsInfo]
    return settingsInformationList    

def getSequenceInfoInformation(configurations):
    descriptionInfo = configurations["info"]["description"]
    slicesInfo = configurations["info"]["slices"]
    fovInfo = configurations["info"]["fov"]
    pelinesInfo = configurations["info"]["pe_lines"]
    seqstringInfo = configurations["info"]["seqstring"]
    reconstructionInfo = configurations["info"]["reconstruction"]
    sequenceInfoInformationList = [descriptionInfo, slicesInfo, fovInfo, 
                                   pelinesInfo, seqstringInfo, 
                                   reconstructionInfo]
    return sequenceInfoInformationList

def getInstructionInformation(boxes, instructionName, instructionHeader):
    printMessageInfo = instructionHeader[0]
    printCounterInfo = instructionHeader[1]
    allStepInformationLists = []
    for box in boxes:
        stepInformationList = getStepInformation(box)
        if box["type"] == "loop" and stepInformationList in \
                                                        allStepInformationLists:
            pass
        else:
            allStepInformationLists.append(stepInformationList)
    instructionInformationList = [instructionName, printMessageInfo,
                                  printCounterInfo, allStepInformationLists]
    return instructionInformationList
            
def getStepInformation(box):
    actionName = box["type"]
    stepInformationList = [actionName]
    match actionName:
        case "run_block":
            blockName = box["name"]
            stepInformationList.extend([blockName])

        case "loop":
            counterInfo = box["block"]
            rangeInfo = box["loop_number"]
            ## TO DO decide either giving directly the all_step_info_lists or
            ## giving a list of step information from which it is extracted.
            derivedBox = {'type': 'run_block', 'name': box["name"]} 
            allStepInformationLists = []
            # for stepInformationList in allStepInformationLists:
            newStepInformationList = getStepInformation(derivedBox)
            allStepInformationLists.append(newStepInformationList)
            stepInformationList.extend([counterInfo, rangeInfo, 
                                        allStepInformationLists])  
            
        case "calc":
            typeInfo = box["inputCalcActionType"]
            floatInfo = box["inputCalcFloat"]
            incrementInfo = box["inputCalcIncrement"]
            stepInformationList.extend([typeInfo, floatInfo, incrementInfo]) 

        case "init":
            gradientInfo = box["inputInitActionGradients"]
            stepInformationList.extend([gradientInfo]) 

        case "sync":
            objectInfo = box["inputSyncObject"]
            objectInformationList = getObjectInformation(typeInfo = actionName, 
                                                         box = box)
            timeInfo = box["inputSyncTime"]
            stepInformationList.extend([objectInfo, objectInformationList,
                                        timeInfo]) 
            
        case "grad":
            axisInfo = box["axis"]
            objectInfo = box["name"]
            objectInformationList = getObjectInformation(typeInfo = actionName, 
                                                         box = box)
            timeInfo = int(float(box["start_time"]))
            stepInformationList.extend([axisInfo, objectInfo, 
                                        objectInformationList, timeInfo]) 
            if str(box["flip_amplitude"]) == "True":
                flipAmplitudeInfo = "flip"
                stepInformationList.extend([flipAmplitudeInfo])
            if str(box["variable_amplitude"]) == "True":
                amplitudeTypeInfo = "equation"
                amplitudeEquationNameInfo = box["equation_info"]["name"]
                stepInformationList.extend([amplitudeTypeInfo, 
                                            amplitudeEquationNameInfo])
                equationInfo = box["equation_info"]["expression"]
                stepInformationList.extend([equationInfo])

        case "rf":
            objectInfo= box["name"]
            objectInformationList = getObjectInformation(typeInfo = actionName, 
                                                         box = box)
            timeInfo = int(float(box["start_time"]))
            addedPhaseTypeInfo = box["rf_added_phase_type"]
            addedPhaseFloatInfo = box["rf_added_phase_float"]
            stepInformationList.extend([objectInfo, objectInformationList, 
                                        timeInfo, addedPhaseTypeInfo, 
                                        addedPhaseFloatInfo])
        
        case "adc":
            objectInfo = box["name"]
            objectInformationList = getObjectInformation(typeInfo = actionName, 
                                                         box = box)
            timeInfo = int(float(box["start_time"]))
            frequencyInfo = box["frequency"]
            phaseInfo = box["phase"]
            addedPhaseTypeInfo = box["adc_added_phase_type"]
            addedPhaseFloatInfo = box["adc_added_phase_float"]
            # TO DO add "header" to the dictionnary
            # mdhInfoList = box["header"]
            mdhInfoList = []
            #### TO DO !!! complete mdhInfoList
            print("passed for now") 
            stepInformationList.extend([objectInfo, objectInformationList, 
                                        timeInfo, frequencyInfo, phaseInfo,
                                        addedPhaseTypeInfo,addedPhaseFloatInfo,
                                        mdhInfoList])
            
        case "mark":
            timeInfo = box["start_time"]
            stepInformationList.extend([timeInfo])

        case "submit":
            pass
        
        case _:
            print("The type " + actionName + " could not be identified.")
    return stepInformationList
            
def getObjectInformation(typeInfo, box):
    objectInformationList = [typeInfo]
    match typeInfo:
        case "rf":
            ## TO DO make the duration step flexible
            durationInfo = len(box["array_info"]["array"])*20
            arrayInfo = box["array_info"]["name"]
            arrayInformationList = getArrayInformation(box = box)
            initPhaseInfo = box["init_phase"]
            thicknessInfo = box["thickness"]
            flipAngleInfo = box["flip_angle"]
            purposeInfo = box["purpose"]
            objectInformationList.extend([durationInfo, arrayInfo, 
                                          arrayInformationList, 
                                          initPhaseInfo, thicknessInfo, 
                                          flipAngleInfo, purposeInfo])
            
        case "grad":
            durationInfo = len(box["array_info"]["array"])*10
            arrayName = box["array_info"]["name"]
            arrayInformationList = getArrayInformation(box = box)
            # TO DO add "tail" to the dictionnary
            # tailInfo = box["tail"]
            tailInfo = 0
            amplitudeInfo = box['amplitude']
            objectInformationList.extend([durationInfo, arrayName, 
                                          arrayInformationList, 
                                          tailInfo, amplitudeInfo])
            
        case "adc":
            durationInfo = box["adc_duration"]*1e3
            samplesInfo = box["samples"]
            dwelltimeInfo = box["dwell_time"]
            objectInformationList.extend([durationInfo, samplesInfo, 
                                          dwelltimeInfo])

        case "sync":
            eventInfo = box["inputSyncEventParam"]
            durationInfo = box["inputSyncDuration"]
            objectInformationList.extend([durationInfo, eventInfo])

        case "init":
            pass

        case "calc":
            pass

        case _:
            print("The type " + typeInfo + " could not be identified.")

    return objectInformationList
            
def getArrayInformation(box):
    # TO DO add "encoding" to the dictionnary
    # encodingInfo = box["encoding"]
    encodingInfo = "text"
    # TO DO add "type" to the dictionnary
    # typeInfo = box["type"]
    typeInfo = "float"
    array = box["array_info"]["array"]
    sizeInfo = len(array)
    dataInfoList = array
    arrayInformationList = [encodingInfo, typeInfo, sizeInfo, dataInfoList]
    return arrayInformationList