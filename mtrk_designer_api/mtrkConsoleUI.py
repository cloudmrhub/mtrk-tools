################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################  

from SDL_read_write.pydanticSDLHandler import *
from sdlFileCreator import *

#############################################################
### User interface interaction
#############################################################

def mtrkConsoleUI(sequence_data):
    sdlInitialize(sequence_data)

    ### file section
    print("*************** - FILE - ***************")
    print("Do you want to provide file information? (yes/no)")
    if(input() == "yes"):
        fileInformationList = getFileInformation()
        completeFileInformation(sequence_data, fileInformationList)
    else:
        print("Default File information used.")

    ### settings section
    print("*************** - SETTINGS - ***************")
    print("Do you want to provide general sequence settings? (yes/no)")
    if(input() == "yes"):
        settingsInformationList = getSequenceSettings()
        completeSequenceSettings(sequence_data, settingsInformationList)
    else:
        print("Default Settings information used.")

    ### info section
    print("*************** - INFORMATION - ***************")
    print("Do you want to provide general sequence information? (yes/no)")
    if(input() == "yes"):
        sequenceInfoInformationList = getSequenceInformation()
        completeSequenceInformation(sequence_data, sequenceInfoInformationList)
    else:
        print("Default Info information used.")

    ### instructions section
    print("*************** - INSTRUCTIONS - ***************")
    answer = "yes"
    while(answer == "yes"):
        print("*** Do you want to add a new instruction? (yes/no)")
        answer = input()
        if(answer == "yes"):
            print("Instruction name (str):")
            instructionName = input()
            addInstruction(sequence_data, instructionName)
            print("Do you want to provide instruction information? (yes/no)")
            if(input() == "yes"):
                instructionInformationList = \
                                      getInstructionInformation(instructionName)
                completeInstructionInformation(sequence_data, instructionInformationList)
                print("instructionToModify = "+str(sequence_data.instructions[instructionName]))
            else:
                print("Default Instruction information used.")
        else:
            print("*******************************************")

    return sequence_data

#############################################################
### Functions to get new values from the user
#############################################################

def getFileInformation():
    print("format (str)")
    formatInfo = input()
    print("version (int)")
    versionInfo = int(input())
    print("measurement (str)")
    measurementInfo = input()
    print("system (str)")
    systemInfo = input()
    fileInformationList = [formatInfo, versionInfo, measurementInfo, systemInfo]
    return fileInformationList

def getSequenceSettings():
    print("readout_os (int)")
    readoutOsInfo = input()
    settingsInformationList = [readoutOsInfo]
    return settingsInformationList

def getSequenceInformation():
    print("description (str)")
    descriptionInfo = input()
    print("slices (int)")
    slicesInfo = int(input())
    print("fov (int)")
    fovInfo = int(input())
    print("pelines (int)")
    pelinesInfo = int(input())
    print("seqstring (str)")
    seqstringInfo = input()
    print("reconstruction (str)")
    reconstructionInfo = input()
    sequenceInfoInformationList = [descriptionInfo, slicesInfo, fovInfo, \
                                   pelinesInfo, seqstringInfo, \
                                   reconstructionInfo]
    return sequenceInfoInformationList

def getInstructionInformation(instructionName):
    print("Message to print (str): ")
    printMessageInfo = input()
    print("Printing counter option (on/off): ")
    printCounterInfo = input()
    stepAnswer = "yes"
    stepIndex = 0
    allStepInformationLists = []
    while(stepAnswer == "yes"):
        print("Do you want to add a new step? (yes/no)")
        stepAnswer = input()
        if(stepAnswer == "yes"):
            print("Do you want to provide step information? (yes/no)")
            if(input() == "yes"):
                newStepInformationList = getStepInformation()
                allStepInformationLists.append(newStepInformationList)
            else:
                print("Default Instruction information used.")
            stepIndex += 1
        else:
            pass
    instructionInformationList = [instructionName, printMessageInfo,\
                                  printCounterInfo, allStepInformationLists]
    return instructionInformationList

def getStepInformation():
    print("Provide step action type: ")
    print("Action (run_block/loop/calc/init/sync/grad/rf/adc/mark/submit): ")
    actionName = input()
    print("Provide information for step of type " + str(actionName) + ": ")
    stepInformationList = [actionName]
    match actionName:
        case "run_block":
            print("block (str)")
            blockName = input()
            print("Do you want to provide block information? (yes/no)")
            blockInformationList = []
            if(input()=="yes"):
                blockInformationList = getInstructionInformation(blockName)
            else:
                print("Default Array information used.")
            stepInformationList.extend([blockName, blockInformationList])
        case "loop":
            print("counter (int)")
            counterInfo = input()
            print("range (int)")
            rangeInfo = input()
            print("steps (Step)")
            stepAnswerLoop = "yes"
            stepIndexLoop = 0
            allStepInformationLists = []
            while(stepAnswerLoop == "yes"):
                print("Do you want to add a new step in the loop? (yes/no)")
                stepAnswerLoop = input()
                nextAnswer = "yes"
                if(stepAnswerLoop == "yes"):
                    print("Do you want to provide step information? (yes/no)")
                    nextAnswer = input()
                    if(nextAnswer == "yes"):
                        newStepInformationList = getStepInformation()
                        allStepInformationLists.append(newStepInformationList)
                    else:
                        print("Default Loop information used.")
                    stepIndexLoop += 1
                else:
                    pass  
            stepInformationList.extend([counterInfo, rangeInfo, allStepInformationLists])  
        case "calc":
            print("type (str)")
            typeInfo = input()
            print("float (float)")
            floatInfo = input()
            print("increment (int)")
            incrementInfo = input() 
            stepInformationList.extend([typeInfo, floatInfo, incrementInfo]) 
        case "init":
            print("gradients (str)")
            gradientInfo = input()
            stepInformationList.extend([gradientInfo]) 
        case "sync":
            print("object (str)")
            objectInfo = input()
            print("Do you want to provide object information? (yes/no)")
            if(input()=="yes"):
                objectInformationList = getObjectInformation(actionName)
            else:
                print("Default Object information used.")
            print("time (int)")
            timeInfo = input()
            stepInformationList.extend([objectInfo, objectInformationList, timeInfo]) 
        case "grad":
            print("axis (slice/read/phase)")
            axisInfo = input()
            print("object (str)")
            objectInfo = input()
            print("Do you want to provide object information? (yes/no)")
            if(input()=="yes"):
                objectInformationList = getObjectInformation(actionName)
            else:
                print("Default Object information used.")
            print("time (int)")
            timeInfo = input() 
            stepInformationList.extend([axisInfo, objectInfo, \
                                        objectInformationList, timeInfo]) 
            print("Do you want to add an amplitude option? (yes/no)")
            if(input()=="yes"):
                print("amplitude option (flip/equation)")
                amplitudeAnswer = input()
                if(amplitudeAnswer=="flip"):
                    flipAmplitudeInfo = "flip"
                    stepInformationList.extend([flipAmplitudeInfo])
                elif(amplitudeAnswer=="equation"):
                    amplitudeTypeInfo = "equation"
                    print("amplitude equation name (str)")
                    amplitudeEquationNameInfo = input()
                    stepInformationList.extend([amplitudeTypeInfo, \
                                                amplitudeEquationNameInfo])
                    print("Do you want to complete equation information? (yes/no)")
                    if(input()=="yes"):
                        print("equation (str)")
                        equationInfo = input()
                        stepInformationList.extend([equationInfo])
            else:
                print("No amplitude option added.")

        case "rf":
            print("object (str)")
            objectInfo = input()
            print("Do you want to provide object information? (yes/no)")
            if(input()=="yes"):
                objectInformationList = getObjectInformation(actionName)
            else:
                print("Default Object information used.")
            print("time (float)")
            timeInfo = input()
            print("added_phase type (str)")
            addedPhaseTypeInfo = input()
            print("added_phase float (float)")
            addedPhaseFloatInfo = input()
            stepInformationList.extend([objectInfo, objectInformationList, \
                                        timeInfo, addedPhaseTypeInfo, \
                                        addedPhaseFloatInfo])
        case "adc":
            print("object (str)")
            objectInfo = input()
            print("Do you want to provide object information? (yes/no)")
            if(input()=="yes"):
                objectInformationList = getObjectInformation(actionName)
            else:
                print("Default Object information used.")
            print("time (float)")
            timeInfo = input()
            print("frequency (int)")
            frequencyInfo = input()
            print("phase (int)")
            phaseInfo = input()
            print("added_phase type (str)")
            addedPhaseTypeInfo = input()
            print("added_phase float (float)")
            addedPhaseFloatInfo = input()
            print("mdh (dict[str, MdhOption])")
            mdhInfoList = []
            #### TO DO !!! complete mdhInfoList
            print("passed for now") 
            stepInformationList.extend([objectInfo, objectInformationList, \
                                        timeInfo, frequencyInfo, phaseInfo,\
                                        addedPhaseTypeInfo,addedPhaseFloatInfo,\
                                        mdhInfoList])
        case "mark":
            print("time (float)")
            timeInfo = input()
            stepInformationList.extend([timeInfo])
        case "submit":
            print("Nothing to customize in submit.")
        case _:
            print("The type " + actionName + " could not be identified.")
    return stepInformationList

def getObjectInformation(typeInfo):
    print("Provide information for object of type " + str(typeInfo) + ": ")
    print("duration (int)")
    durationInfo = input()
    objectInformationList = [typeInfo, durationInfo]
    match typeInfo:
        case "rf":
            print("array (str)")
            arrayInfo = input()
            print("Do you want to provide array information? (yes/no)")
            if(input()=="yes"):
                arrayInformationList = getArrayInformation()
            else:
                print("Default Array information used.")
            print("initial_phase (int)")
            initPhaseInfo = input()
            print("thickness (int)")
            thicknessInfo = input()
            print("flipangle (int)")
            flipAngleInfo = input()
            print("purpose (str)")
            purposeInfo = input()
            objectInformationList.extend([arrayInfo, arrayInformationList, \
                                          initPhaseInfo, thicknessInfo, \
                                          flipAngleInfo, purposeInfo])
        case "grad":
            print("array (str)")
            arrayName = input()
            print("Do you want to provide array information? (yes/no)")
            if(input()=="yes"):
                arrayInformationList = getArrayInformation()
            else:
                print("Default Array information used.")
            print("tail (int)")
            tailInfo = input()
            print("amplitude (float)")
            amplitudeInfo = input()
            objectInformationList.extend([arrayName, arrayInformationList, \
                                          tailInfo, amplitudeInfo])
        case "adc":
            print("samples (int)")
            samplesInfo = input()
            print("dwelltime (int)")
            dwelltimeInfo = input()
            objectInformationList.extend([samplesInfo, dwelltimeInfo])
        case "sync":
            print("event (str)")
            eventInfo = input()
            objectInformationList.extend([eventInfo])
        case _:
            print("The type " + typeInfo + " could not be identified.")
    return objectInformationList

def getArrayInformation():
    print("encoding (str)")
    encodingInfo = input()
    print("type (str)")
    typeInfo = input()
    print("size (int)")
    sizeInfo = input()
    print("data (float, float, ...)")
    dataInfoList = [float(elem) for elem in input().split(", ")]
    arrayInformationList = [encodingInfo, typeInfo, sizeInfo, dataInfoList]
    print("+-+-+ getArrayInfo " + str(arrayInformationList))
    return arrayInformationList
