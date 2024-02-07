################################################################################
### mtrk project - Transition from backend to UI                             ###
### Version 1.0.0                                                            ###
### Anais Artiges and the mtrk project team at NYU - 01/31/2024              ###
################################################################################  

import json
import jsbeautifier
import re
import ast
from pprint import pprint
from devtools import debug
from sdlFileCreator import *

#############################################################
### Creating SDL file from web-based UI
#############################################################

def create_sdl_from_ui_inputs(boxes):
    # Initialize SDL file
    # TO DO - need to intialize without loading file
    with open('/vagrant/miniflash.json') as sdlFile:
        sdlData = json.load(sdlFile)
        sequence_data = PulseSequence(**sdlData)
    sdlInitialize(sequence_data)

    updateSDLFile(sequence_data, boxes)
    
    ### writing of json schema to SDL file with formatting options
    with open('output.mtrk', 'w') as sdlFileOut:
        options = jsbeautifier.default_options()
        options.indent_size = 4
        data_to_print = jsbeautifier.beautify(json.dumps(sequence_data.model_dump(mode="json")), options)
        sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic

def updateSDLFile(sequence_data, boxes):
    instructionName = "dummy_instruction_name"
    addInstruction(sequence_data, instructionName)
    instructionInformationList = getInstructionInformation(
            sequence_data = sequence_data, 
            instructionToModify = sequence_data.instructions[instructionName], 
            boxes = boxes)
    completeInstructionInformation(sequence_data = sequence_data, 
                                   instructionInformationList = instructionInformationList)

def create_sdl_from_ui_inputs(boxes):
    # Initialize SDL file
    # TO DO - need to intialize without loading file
    with open('/vagrant/miniflash.json') as sdlFile:
        sdlData = json.load(sdlFile)
        sequence_data = PulseSequence(**sdlData)
    sdlInitialize(sequence_data)

    updateSDLFile(sequence_data, boxes)
    
    ### writing of json schema to SDL file with formatting options
    with open('output.mtrk', 'w') as sdlFileOut:
        options = jsbeautifier.default_options()
        options.indent_size = 4
        data_to_print = jsbeautifier.beautify(json.dumps(sequence_data.model_dump(mode="json")), options)
        sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic
        
############################################################

def getInstructionInformation(sequence_data, instructionToModify, boxes):
    stepIndex = 0
    for box in boxes:
        addStep(instructionToModify = instructionToModify, 
                stepIndex = stepIndex, 
                actionName = box["type"])
        stepToModify = instructionToModify.steps[stepIndex]
        completeStepInformation(sequence_data, stepToModify, "Instruction", box)
        stepIndex += 1
            
def getStepInformation(box):
    actionName = box["type"]
    stepInformationList = [actionName]
    match actionName:
        ## TO DO: add other types of supported actionName (follow example in console UI)
        case "grad":
            axisInfo = box["axis"]
            objectInfo = box["name"]
            objectInformationList = getObjectInformation(typeInfo = actionName, 
                                                         box = box)
            timeInfo = int(float(box["start_time"]))
            stepInformationList.extend([axisInfo, objectInfo, \
                                        objectInformationList, timeInfo]) 
            ## TO DO: add amplitude information (follow example in console UI)

        case "rf":
            objectInfo= box["name"]
            objectInformationList = getObjectInformation(typeInfo = actionName, 
                                                         box = box)
            timeInfo = int(float(box["start_time"]))
            ### begin: not used for now
            addedPhaseTypeInfo = "duffmy_phase_type"
            addedPhaseFloatInfo = 0.0
            ### end: not used for now
            stepInformationList.extend([objectInfo, objectInformationList, \
                                        timeInfo, addedPhaseTypeInfo, \
                                        addedPhaseFloatInfo])
        
        case "adc":
            objectInfo = box["name"]
            objectInformationList = getObjectInformation(typeInfo = actionName, 
                                                         box = box)
            timeInfo = int(float(box["start_time"]))
            ### begin: not used for now
            frequencyInfo = 0
            phaseInfo = 0
            addedPhaseTypeInfo = "dummy_phase"
            addedPhaseFloatInfo = 0.0
            mdhInfoList = []
            #### TO DO !!! complete mdhInfoList
            ## WARNING: the above TO DO is true for all codes for now (02/07/24)
            print("passed for now") 
            ### end: not used for now
            stepInformationList.extend([objectInfo, objectInformationList, \
                                        timeInfo, frequencyInfo, phaseInfo,\
                                        addedPhaseTypeInfo,addedPhaseFloatInfo,\
                                        mdhInfoList])
        
        case _:
            print("The type " + actionName + " could not be identified.")
    return stepInformationList
            
def getObjectInformation(typeInfo, box):
    durationInfo = len(box["array"])
    objectInformationList = [typeInfo, durationInfo]
    match typeInfo:
        case "rf":
            arrayInfo = typeInfo + "_default_array"
            arrayInformationList = getArrayInformation(box = box)
            ### begin: not used for now
            initPhaseInfo = 0
            thicknessInfo = 0
            flipAngleInfo = 0
            purposeInfo = "dummy_purpose"
            ### end: not used for now
            objectInformationList.extend([arrayInfo, arrayInformationList, \
                                          initPhaseInfo, thicknessInfo, \
                                          flipAngleInfo, purposeInfo])
        case "grad":
            arrayName = typeInfo + "_default_array"
            arrayInformationList = getArrayInformation(box = box)
            ### begin: not used for now
            tailInfo = 0
            ### end: not used for now
            amplitudeInfo = box['amplitude']
            objectInformationList.extend([arrayName, arrayInformationList, \
                                          tailInfo, amplitudeInfo])
        case "adc":
            ### begin: not used for now
            samplesInfo = 0
            dwelltimeInfo = 0
            ### end: not used for now
            objectInformationList.extend([samplesInfo, dwelltimeInfo])
        case "sync":
            pass
            ### begin: not used for now
            eventInfo = "dummy_event"
            ### end: not used for now
            objectInformationList.extend([eventInfo])
        case _:
            print("The type " + typeInfo + " could not be identified.")
    return objectInformationList
            
def getArrayInformation(box):
    # TO DO: change the fixed encoding and type info.
    encodingInfo = "text"
    typeInfo = "float"
    array = box['array']
    sizeInfo = len(array)
    dataInfoList = array
    arrayInformationList = [encodingInfo, typeInfo, sizeInfo, dataInfoList]
    return arrayInformationList