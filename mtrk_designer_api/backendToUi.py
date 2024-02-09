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
    with open('C:/Users/artiga02/mtrk_seq/examples/miniflash.mtrk') as sdlFile:
        sdlData = json.load(sdlFile)
        sequence_data = PulseSequence(**sdlData)
    sdlInitialize(sequence_data)

    updateSDLFile(sequence_data, boxes)
    
    ### writing of json schema to SDL file with formatting options
    with open('output.mtrk', 'w') as sdlFileOut:
        options = jsbeautifier.default_options()
        options.indent_size = 4
        data_to_print = jsbeautifier.beautify(\
                     json.dumps(sequence_data.model_dump(mode="json")), options)
        sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) 
        #purely aesthetic

def updateSDLFile(sequence_data, boxes):
    instructionName = "dummy_instruction_name"
    addInstruction(sequence_data, instructionName)
    instructionInformationList = getInstructionInformation(boxes = boxes,
                                                           instructionName = \
                                                                instructionName)
    completeInstructionInformation(sequence_data = sequence_data, 
                                   instructionInformationList = \
                                                     instructionInformationList)

        
#############################################################
### Functions to get new values from the web-based UI
#############################################################

def getInstructionInformation(boxes, instructionName):
    # TO DO add "message" to the dictionnary
    # printMessageInfo = box["message"]
    printMessageInfo = "dummy_message"
    # TO DO add "counter_on_off" to the dictionnary
    # printCounterInfo = box["counter_on_off"]
    printCounterInfo = "off"
    allStepInformationLists = []
    for box in boxes:
        stepInformationList = getStepInformation(box)
        allStepInformationLists.append(stepInformationList)
    instructionInformationList = [instructionName, printMessageInfo,\
                                  printCounterInfo, allStepInformationLists]
    return instructionInformationList
            
def getStepInformation(box):
    actionName = box["type"]
    stepInformationList = [actionName]
    match actionName:
        case "run_block":
            # TO DO add "block_name" to the dictionnary
            # allStepInformationLists = box["block_name"]
            blockName = "dummy_block_name"
            blockInformationList = getInstructionInformation(blockName)
            stepInformationList.extend([blockName, blockInformationList])

        case "loop":
            # TO DO add "counter_number" to the dictionnary
            # allStepInformationLists = box["counter_number"]
            counterInfo = 1
            # TO DO add "counter_range" to the dictionnary
            # allStepInformationLists = box["counter_range"]
            rangeInfo = 1
            # TO DO add "all_step_info_lists" to the dictionnary
            # allStepInformationLists = box["all_step_info_lists"]
            # TO DO We need to decide either giving directly the 
            # all_step_info_lists or giving a list of step information from 
            # which it is extracted. 
            allStepInformationLists = []
            for stepInformationList in allStepInformationLists:
                newStepInformationList = getStepInformation()
                allStepInformationLists.append(newStepInformationList)
            stepInformationList.extend([counterInfo, rangeInfo, 
                                        allStepInformationLists])  
            
        case "calc":
            # TO DO add "type" to the dictionnary
            # allStepInformationLists = box["type"]
            typeInfo = "dummy_type"
            # TO DO add "float" to the dictionnary
            # allStepInformationLists = box["float"]
            floatInfo = 0.0
            # TO DO add "increment" to the dictionnary
            # allStepInformationLists = box["increment"]
            incrementInfo = 0
            stepInformationList.extend([typeInfo, floatInfo, incrementInfo]) 

        case "init":
            # TO DO add "gradient_mode" to the dictionnary
            # allStepInformationLists = box["gradient_mode"]
            gradientInfo = "dummy_gradient_mode"
            stepInformationList.extend([gradientInfo]) 

        case "sync":
            # TO DO add "object_name" to the dictionnary
            # allStepInformationLists = box["object_name"]
            objectInfo = "dummy_object_name"
            objectInformationList = getObjectInformation(actionName)
            # TO DO add "time" to the dictionnary
            # allStepInformationLists = box["time"]
            timeInfo = 0
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
            # TO DO add "amplitude_flip" to the dictionnary
            # if(box["amplitude_flip"]=="true"):
            #     flipAmplitudeInfo = "flip"
            #     stepInformationList.extend([flipAmplitudeInfo])
            if(box["variable_amplitude"]=="true"):
                amplitudeTypeInfo = "equation"
                # TO DO add "equation_name" to the dictionnary
                # amplitudeEquationNameInfo = box["equation_name"]
                amplitudeEquationNameInfo = "dummy_eq_name"
                stepInformationList.extend([amplitudeTypeInfo, 
                                            amplitudeEquationNameInfo])
                # TO DO add "equation_expression" to the dictionnary
                # equationInfo = box["equation_expression"]
                equationInfo = "dummy_equation_expression"
                stepInformationList.extend([equationInfo])

        case "rf":
            objectInfo= box["name"]
            objectInformationList = getObjectInformation(typeInfo = actionName, 
                                                         box = box)
            timeInfo = int(float(box["start_time"]))
            # TO DO add "rf_added_phase_type" to the dictionnary
            # addedPhaseTypeInfo = box["rf_added_phase_type"]
            addedPhaseTypeInfo = "dummy_phase_type"
            # TO DO add "rf_added_phase_float" to the dictionnary
            # addedPhaseFloatInfo = box["rf_added_phase_float"]
            addedPhaseFloatInfo = 0.0
            stepInformationList.extend([objectInfo, objectInformationList, \
                                        timeInfo, addedPhaseTypeInfo, \
                                        addedPhaseFloatInfo])
        
        case "adc":
            objectInfo = box["name"]
            objectInformationList = getObjectInformation(typeInfo = actionName, 
                                                         box = box)
            timeInfo = int(float(box["start_time"]))
            # TO DO add "frequency" to the dictionnary
            # frequencyInfo = box["frequency"]
            frequencyInfo = 0
            # TO DO add "phase" to the dictionnary
            # phaseInfo = box["phase"]
            phaseInfo = 0
            # TO DO add "rf_added_phase_float" to the dictionnary
            # addedPhaseTypeInfo = box["adc_added_phase_type"]
            addedPhaseTypeInfo = "dummy_phase"
            # TO DO add "rf_added_phase_float" to the dictionnary
            # addedPhaseFloatInfo = box["adc_added_phase_float"]
            addedPhaseFloatInfo = 0.0
            # TO DO add "mdh" to the dictionnary
            # mdhInfoList = box["mdh"]
            mdhInfoList = []
            #### TO DO !!! complete mdhInfoList
            ## WARNING: the above TO DO is true for all codes for now (02/07/24)
            print("passed for now") 
            ### end: not used for now
            stepInformationList.extend([objectInfo, objectInformationList, \
                                        timeInfo, frequencyInfo, phaseInfo,\
                                        addedPhaseTypeInfo,addedPhaseFloatInfo,\
                                        mdhInfoList])
            
        case "mark":
            # TO DO add "time" to the dictionnary
            # mdhInfoList = box["time"]
            timeInfo = 0.0
            stepInformationList.extend([timeInfo])

        case "submit":
            pass
        
        case _:
            print("The type " + actionName + " could not be identified.")
    return stepInformationList
            
def getObjectInformation(typeInfo, box):
    durationInfo = len(box["array_info"]["array"])
    objectInformationList = [typeInfo, durationInfo]
    match typeInfo:
        case "rf":
            arrayInfo = typeInfo + "_default_array"
            arrayInformationList = getArrayInformation(box = box)
            # TO DO add "init_phase" to the dictionnary
            # initPhaseInfo = box["init_phase"]
            initPhaseInfo = 0
            # TO DO add "thickness" to the dictionnary
            # thicknessInfo = box["thickness"]
            thicknessInfo = 0
            # TO DO add "flip_angle" to the dictionnary
            # flipAngleInfo = box["flip_angle"]
            flipAngleInfo = 0
            # TO DO add "purpose" to the dictionnary
            # purposeInfo = box["purpose"]
            purposeInfo = "dummy_purpose"
            objectInformationList.extend([arrayInfo, arrayInformationList, \
                                          initPhaseInfo, thicknessInfo, \
                                          flipAngleInfo, purposeInfo])
            
        case "grad":
            arrayName = typeInfo + "_default_array"
            arrayInformationList = getArrayInformation(box = box)
            # TO DO add "tail" to the dictionnary
            # tailInfo = box["tail"]
            tailInfo = 0
            amplitudeInfo = box['amplitude']
            objectInformationList.extend([arrayName, arrayInformationList, \
                                          tailInfo, amplitudeInfo])
            
        case "adc":
            # TO DO add "samples" to the dictionnary
            # samplesInfo = box["samples"]
            samplesInfo = 0
            # TO DO add "dwell_time" to the dictionnary
            # dwelltimeInfo = box["dwell_time"]
            dwelltimeInfo = 0
            objectInformationList.extend([samplesInfo, dwelltimeInfo])

        case "sync":
            # TO DO add "event" to the dictionnary
            # eventInfo = box["event"]
            eventInfo = "dummy_event"
            objectInformationList.extend([eventInfo])

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