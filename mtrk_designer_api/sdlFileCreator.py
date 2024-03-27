################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################  

from SDL_read_write.pydanticSDLHandler import *

#############################################################
### Functions to create SDL file objects
#############################################################

### SDL file initialization with mandatory sections and default values
def sdlInitialize(sequence_data):
    sequence_data.file = File()
    sequence_data.infos = Info()
    sequence_data.settings = Settings()
    sequence_data.instructions = {}
    sequence_data.objects = {}
    sequence_data.arrays = {}
    sequence_data.equations = {}


def addInstruction(sequence_data, instructionName):
    sequence_data.instructions[instructionName] = Instruction(steps=[])


def addStep(instructionToModify, stepIndex, actionName):
    try:
        match actionName:
            case "run_block":
                instructionToModify.steps.append(RunBlock())
                print("Disclaimer: no actual block created here, it will be created if you provide information for the step.")
            case "loop":
                instructionToModify.steps.append(Loop(steps=[]))
            case "calc":
                instructionToModify.steps.append(Calc())
            case "init":
                instructionToModify.steps.append(Init())
            case "sync":
                instructionToModify.steps.append(Sync())
            case "grad":
                instructionToModify.steps.append(Grad())
            case "rf":
                instructionToModify.steps.append( Rf(added_phase = AddedPhase()))
            case "adc":
                instructionToModify.steps.append( Adc(added_phase = AddedPhase(), \
                                                                            mdh={}))
                # mdhOptAnswer = "yes"
                # while(mdhOptAnswer == "yes"):
                #     print("Do you want to add a new MDH option? (yes/no)")
                #     mdhOptAnswer = input()
                #     if(mdhOptAnswer == "yes"):
                #         addMdhOption(instructionToModify.steps, stepIndex)
                #     else:
                #         pass
            case "mark":
                instructionToModify.steps.append(Mark())
            case "submit":
                instructionToModify.steps.append(Submit())
            case _:
                raise ValueError(actionName + " is not available")
    except ValueError as e:
        print(str(e))


def addMdhOption(stepToModify, stepIndex):
    print("Provide MDH option information: ")
    print("MDH option type (str): ")
    stepToModify[stepIndex].mdh[input()] = MdhOption()


def addObject(sequence_data, objectName, typeName):
    try:
        match typeName:
            case "rf":
                sequence_data.objects[objectName] = RfExcitation()
            case "grad":
                sequence_data.objects[objectName] = GradientObject()
            case "adc":
                sequence_data.objects[objectName] = AdcReadout()
            case "sync":
                sequence_data.objects[objectName] = Ttl()
            case _:
                raise ValueError(typeName + " is not available")
    except ValueError as e:
        print(str(e))


def addArray(sequence_data, arrayName):
    sequence_data.arrays[arrayName] = GradientTemplate()


def addEquation(sequence_data, equationName):
    sequence_data.equations[equationName] = Equation()


#############################################################
### Functions to fill SDL file objects with new values
#############################################################

def completeFileInformation(sequence_data, fileInformationList):
    ## fileInformationList = [formatInfo, versionInfo, measurementInfo, 
    ##                        systemInfo]
    if(fileInformationList != []):
        sequence_data.file = File(format = fileInformationList[0], 
                                  version = int(fileInformationList[1]), 
                                  measurement = fileInformationList[2], 
                                  system = fileInformationList[3])

def completeSequenceSettings(sequence_data, settingsInformationList):
    ## settingsInformationList = [readoutOsInfo]
    if(settingsInformationList != []):
        sequence_data.settings = Settings(readout_os = \
                                                     settingsInformationList[0])

def completeSequenceInformation(sequence_data, sequenceInfoInformationList):
    ## sequenceInfoInformationList = [descriptionInfo, slicesInfo, fovInfo, 
    ##                                pelinesInfo, seqstringInfo, 
    ##                                reconstructionInfo]
    if(sequenceInfoInformationList != []):
        sequence_data.infos = Info(
                               description = sequenceInfoInformationList[0], 
                               slices = int(sequenceInfoInformationList[1]), 
                               fov = int(sequenceInfoInformationList[2]),  
                               pelines = int(sequenceInfoInformationList[3]), 
                               seqstring = sequenceInfoInformationList[4],
                               reconstruction = sequenceInfoInformationList[5])

def completeInstructionInformation(sequence_data, instructionInformationList):
    ## instructionInformationList = [instructionName, printMessageInfo, 
    ##                               printCounterInfo, allStepInformationLists]
    if(instructionInformationList != []):
        instructionToModify = \
                       sequence_data.instructions[instructionInformationList[0]]
        instructionToModify.print_message = instructionInformationList[1]
        printCounterOption = instructionInformationList[2]
        if(printCounterOption=="on" or printCounterOption=="off"):
            instructionToModify.print_counter = printCounterOption
        else:
            print(printCounterOption + 
                  " is not valid. It should be 'on' or 'off'.")
        allStepInformationLists = []
        for instruction in instructionInformationList[3]:
            if instruction == ['Block']:
                print("+-+-+ Block passed")
            else:
                allStepInformationLists.append(instruction)
        for stepIndex in range(0, len(allStepInformationLists)):
            ## stepInformationList = [actionName, actionSpecificElements...]
            addStep(instructionToModify = instructionToModify, 
                    stepIndex = stepIndex, 
                    actionName = allStepInformationLists[stepIndex][0])
            stepToModify = instructionToModify.steps[stepIndex]
            completeStepInformation(sequence_data = sequence_data, 
                                    stepToModify = stepToModify, 
                                    stepInformationList = \
                                       allStepInformationLists[stepIndex])

def completeStepInformation(sequence_data, stepToModify, stepInformationList):
    ## stepInformationList = [actionName, actionSpecificElements...]
    if(stepInformationList != []):
        actionInfo = stepInformationList[0]
        match actionInfo:
            case "run_block":
                stepToModify.block = stepInformationList[1]
                ## stepInformationList = [actionName, blockName, 
                ##                        blockInformationList]
                ## NEEDED for console UI
                # stepToModify.block= stepInformationList[1]
                # addInstruction(sequence_data, stepToModify.block)
                # if(stepInformationList[2]!= []):
                #     completeInstructionInformation(
                #                                sequence_data = sequence_data, 
                #                                instructionInformationList = \
                #                                          stepInformationList[2])
                # else:
                #     print("Default Array information used.")
            case "loop":
                ## stepInformationList = [actionName, counterInfo, rangeInfo, 
                ##                        allStepInformationLists]
                savedStepToModify = stepToModify
                savedStepToModify.counter = stepInformationList[1]
                savedStepToModify.range= stepInformationList[2]
                for stepIndexLoop in range(0, len(stepInformationList[3])):
                    addStep(instructionToModify = savedStepToModify, 
                            stepIndex = stepIndexLoop, 
                            actionName = stepInformationList[3][stepIndexLoop][0])
                    completeStepInformation(sequence_data = sequence_data, 
                                            stepToModify = \
                                         savedStepToModify.steps[stepIndexLoop], 
                                            stepInformationList = \
                                          stepInformationList[3][stepIndexLoop]) 
                stepToModify = savedStepToModify  
            case "calc":
                ## stepInformationList = [actionName, typeInfo, floatInfo, 
                ##                        incrementInfo]
                stepToModify.type = stepInformationList[1]
                stepToModify.float= stepInformationList[2]
                stepToModify.increment = stepInformationList[3] 
            case "init":
                ## stepInformationList = [actionName, gradientInfo]
                stepToModify.gradients = stepInformationList[1]
            case "sync":
                ## stepInformationList = [actionName, objectInfo, 
                ##                        objectInformationList, timeInfo]
                stepToModify.object = stepInformationList[1]
                if stepToModify.object not in sequence_data.objects:
                    addObject(sequence_data=sequence_data, 
                            objectName=stepToModify.object,
                            typeName = "sync")
                completeObjectInformation(sequence_data = sequence_data, 
                                          objectName = stepToModify.object,
                                          objectInformationList = \
                                                         stepInformationList[2])
                stepToModify.time = stepInformationList[3]
            case "grad":
                ## stepInformationList = [actionName, axisInfo, objectInfo, 
                ##                        objectInformationList, timeInfo]
                stepToModify.axis = stepInformationList[1]
                stepToModify.object= stepInformationList[2]
                if stepToModify.object not in sequence_data.objects:
                    addObject(sequence_data=sequence_data, 
                              objectName=stepToModify.object,
                              typeName = "grad")
                completeObjectInformation(sequence_data = sequence_data, 
                                          objectName = stepToModify.object,
                                          objectInformationList = \
                                                         stepInformationList[3])
                stepToModify.time = stepInformationList[4]
                if(len(stepInformationList) >= 6):
                    amplitudeAnswer = stepInformationList[5]
                    if(amplitudeAnswer=="flip"):
                        ## stepInformationList = [actionName, axisInfo, objectInfo, 
                        ##                        objectInformationList, timeInfo, 
                        ##                        flipAmplitudeInfo]
                        stepToModify.amplitude = "flip"
                    elif(amplitudeAnswer=="equation"):
                        ## stepInformationList = [actionName, axisInfo, objectInfo, 
                        ##                        objectInformationList, timeInfo, 
                        ##                        amplitudeTypeInfo, 
                        ##                        amplitudeEquationNameInfo]
                        stepToModify.amplitude = Amplitude()
                        stepToModify.amplitude.type = stepInformationList[5]
                        stepToModify.amplitude.equation = stepInformationList[6]
                        addEquation(sequence_data = sequence_data, 
                                equationName = stepToModify.amplitude.equation)
                        if(len(stepInformationList) == 8):
                            ## stepInformationList = [actionName, axisInfo, 
                            ##                        objectInfo, 
                            ##                        objectInformationList, 
                            ##                        timeInfo, amplitudeTypeInfo, 
                            ##                        amplitudeEquationNameInfo, 
                            ##                        equationInfo]
                            sequence_data.equations[\
                                stepToModify.amplitude.equation].equation = \
                                                          stepInformationList[7]
                else:
                    print("No amplitude option added.")

            case "rf":
                ## stepInformationList = [actionName, objectInfo, 
                ##                        objectInformationList, timeInfo, 
                ##                        addedPhaseTypeInfo, addedPhaseFloatInfo]
                stepToModify.object= stepInformationList[1]
                if stepToModify.object not in sequence_data.objects:
                    addObject(sequence_data=sequence_data, 
                              objectName=stepToModify.object,
                              typeName = "rf")
                completeObjectInformation(sequence_data = sequence_data, 
                                          objectName = stepToModify.object,
                                          objectInformationList = \
                                                         stepInformationList[2])
                stepToModify.time = stepInformationList[3]
                stepToModify.added_phase = AddedPhase()
                stepToModify.added_phase.type = stepInformationList[4]
                stepToModify.added_phase.float = stepInformationList[5]

            case "adc":
                ## stepInformationList = [actionName, objectInfo, 
                ##                        objectInformationList, timeInfo, 
                ##                        frequencyInfo, phaseInfo,
                ##                        addedPhaseTypeInfo, addedPhaseFloatInfo,
                ##                        mdhInfoList]
                stepToModify.object= stepInformationList[1]
                if stepToModify.object not in sequence_data.objects:
                    addObject(sequence_data=sequence_data, 
                              objectName=stepToModify.object,
                              typeName = "adc")
                completeObjectInformation(sequence_data = sequence_data, 
                                          objectName = stepToModify.object,
                                          objectInformationList = \
                                                         stepInformationList[2])
                stepToModify.time = stepInformationList[3]
                stepToModify.frequency = stepInformationList[4]
                stepToModify.phase= stepInformationList[5]
                stepToModify.added_phase = AddedPhase()
                stepToModify.added_phase.type = stepInformationList[6]
                stepToModify.added_phase.float = stepInformationList[7]
                ## TO DO !!! mdhInfoList = stepInformationList[8]
                print("passed for now") 
            case "mark":
                ## stepInformationList = [actionName, timeInfo]
                stepToModify.time = stepInformationList[1]
            case "submit":
                pass
            case _:
                print("The type " + actionInfo + " could not be identified.")


def completeObjectInformation(sequence_data, objectName, objectInformationList):
    ## objectInformationList = [typeInfo, durationInfo, objectSpecificInfo...]
    if(objectInformationList != []):
        typeInfo = objectInformationList[0]
        durationInfo = objectInformationList[1]
        match typeInfo:
            case "rf":
                ## objectInformationList = [typeInfo, durationInfo, arrayInfo, 
                ##                          arrayInformationList, initPhaseInfo, 
                ##                          thicknessInfo, flipAngleInfo, 
                ##                          purposeInfo]
                arrayInfo = objectInformationList[2]
                if arrayInfo not in sequence_data.arrays:
                    addArray(sequence_data = sequence_data, 
                             arrayName = arrayInfo)
                completeArrayInformation(sequence_data = sequence_data, 
                                         arrayName = arrayInfo,
                                         arrayInformationList = \
                                                       objectInformationList[3])
                initPhaseInfo = objectInformationList[4]
                thicknessInfo = objectInformationList[5]
                flipangleInfo = objectInformationList[6]
                purposeInfo = objectInformationList[7]
                sequence_data.objects[objectName]=RfExcitation( 
                                                duration = durationInfo, 
                                                array = arrayInfo, 
                                                initial_phase =  initPhaseInfo, 
                                                thickness = thicknessInfo, 
                                                flipangle = flipangleInfo, 
                                                purpose = purposeInfo) 
            case "grad":
                ## objectInformationList = [arrayInfo, durationInfo, 
                ##                          arrayName, arrayInformationList, 
                ##                          tailInfo, amplitudeInfo]
                arrayInfo = objectInformationList[2]
                if arrayInfo not in sequence_data.arrays:
                    addArray(sequence_data = sequence_data, 
                             arrayName = arrayInfo)
                completeArrayInformation(sequence_data = sequence_data, 
                                         arrayName = arrayInfo,
                                         arrayInformationList = \
                                                       objectInformationList[3])
                tailInfo = objectInformationList[4]
                amplitudeInfo = objectInformationList[5]
                sequence_data.objects[objectName]=GradientObject(
                                                    duration = durationInfo, 
                                                    array = arrayInfo,
                                                    tail = tailInfo, 
                                                    amplitude = amplitudeInfo) 
            case "adc":
                ## objectInformationList = [arrayInfo, durationInfo, samplesInfo, 
                ##                          dwelltimeInfo]
                samplesInfo = objectInformationList[2]
                dwelltimeInfo = objectInformationList[3]
                sequence_data.objects[objectName]=AdcReadout( 
                                                    duration = durationInfo, 
                                                    samples = samplesInfo, 
                                                    dwelltime = dwelltimeInfo) 
            case "sync":
                ## objectInformationList = [arrayInfo, durationInfo, eventInfo]
                eventInfo = objectInformationList[2]
                sequence_data.objects[objectName]=Ttl(duration = durationInfo, 
                                                      event = eventInfo) 
            case _:
                print("The type " + typeInfo + " could not be identified.")


def completeArrayInformation(sequence_data, arrayName, arrayInformationList):
    ## arrayInformationList = [encodingInfo, typeInfo, sizeInfo, dataInfoList]
    if(arrayInformationList != []):
        encodingInfo = arrayInformationList[0]
        typeInfo = arrayInformationList[1]
        sizeInfo = int(arrayInformationList[2])
        dataInfo = arrayInformationList[3]
        sequence_data.arrays[arrayName] = GradientTemplate( encoding = encodingInfo, 
                                                            type = typeInfo, 
                                                            size = sizeInfo, 
                                                            data = dataInfo)