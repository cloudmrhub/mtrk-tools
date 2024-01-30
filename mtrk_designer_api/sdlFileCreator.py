################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 1.0.0                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################  

from SDL_read_write.pydanticSDLHandler import *

#############################################################
### Creating SDL file from web-based UI
#############################################################

# def create_sdl_from_ui_inputs(boxes):
#     # Initialize SDL file
#     # TO DO - need to intialize without loading file
#     with open('/vagrant/miniflash.json') as sdlFile:
#         sdlData = json.load(sdlFile)
#         sequence_data = PulseSequence(**sdlData)
#     sdlInitialize(sequence_data)

#     updateSDLFile(sequence_data, boxes)
    
#     ### writing of json schema to SDL file with formatting options
#     with open('output.mtrk', 'w') as sdlFileOut:
#         options = jsbeautifier.default_options()
#         options.indent_size = 4
#         data_to_print = jsbeautifier.beautify(json.dumps(sequence_data.model_dump(mode="json")), options)
#         sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic

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

def addStep(instructionToModify, stepIndex, actionName, mdhOptions):
    match actionName:
        case "run_block":
            instructionToModify.steps.append(RunBlock())
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
            for option in mdhOptions:
                addMdhOption(instructionToModify.steps, stepIndex, option)
        case "mark":
            instructionToModify.steps.append(Mark())
        case "submit":
            instructionToModify.steps.append(Submit())
        case _: 
            print(actionName + " is not available")    


def addMdhOption(stepToModify, stepIndex, mdhOptionType):
    stepToModify[stepIndex].mdh[mdhOptionType] = MdhOption()


def addObject(sequence_data, objectName, objectType):
    match objectType:
        case "rf":
           sequence_data.objects[objectName]=RfExcitation() 
        case "grad":
            sequence_data.objects[objectName]=GradientObject() 
        case "adc":
            sequence_data.objects[objectName]=AdcReadout() 
        case "sync":
            sequence_data.objects[objectName]=Ttl() 
        case _:
            print(objectType + " is not available")


def addArray(sequence_data, arrayName):
    sequence_data.arrays[arrayName] = GradientTemplate()


def addEquation(sequence_data, equationName):
    sequence_data.equations[equationName] = Equation()


#############################################################
### Functions to fill SDL file objects with new values
#############################################################

def completeFileInformation(sequence_data, fileInformationList):
    # fileInformationList = [formatInfo, versionInfo, measurementInfo, 
    #                        systemInfo]
    sequence_data.file = File(format = fileInformationList[0], version = fileInformationList[1], \
                             measurement = fileInformationList[2], system = fileInformationList[3])

def completeSequenceSettings(sequence_data, readoutOsInfo):
    sequence_data.settings = Settings(readout_os = readoutOsInfo)

def completeSequenceInformation(sequence_data, sequenceInformationList):
    # sequenceInformationList = [descriptionInfo, slicesInfo, fovInfo, 
    #                            pelinesInfo, seqstringInfo, reconstructionInfo]
    sequence_data.infos = Info(description = sequenceInformationList[0], \
                               slices = sequenceInformationList[1], fov = sequenceInformationList[2],  \
                               pelines = sequenceInformationList[3], seqstring = sequenceInformationList[4],\
                               reconstruction = sequenceInformationList[5])


def completeInstructionInformation(sequence_data, instructionToModify, messageInfo, printCounterOption, stepList):
    instructionToModify.print_message = messageInfo
    if(printCounterOption=="on" or printCounterOption=="off"):
        instructionToModify.print_counter = printCounterOption
    else:
        print(printCounterOption + " is not valid.")
    stepIndex = 0
    for stepIndex in range(0, len(stepList)):
        addStep(instructionToModify, stepIndex)
        stepToModify = instructionToModify.steps[stepIndex]
        completeStepInformation(sequence_data, stepToModify, "Instruction")


def completeStepInformation(sequence_data, stepToModify, actionInfo, actionArray):
    match actionInfo:
        case "run_block":
            # actionArray = [blockName]
            stepToModify.block= actionArray[0]
            addInstruction(sequence_data, stepToModify.block)
            completeInstructionInformation(sequence_data=sequence_data, instructionToModify=sequence_data.instructions[stepToModify.block])
        
        case "loop":
            # actionArray = [loopCounter, loopRange, loopStepList]
            savedStepToModify = stepToModify
            savedStepToModify.counter = actionArray[0]
            savedStepToModify.range= actionArray[1]
            stepIndexLoop = 0
            # TO DO check for issues when adding steps inside loops
            for step in actionArray[2]:
                addStep(savedStepToModify, stepIndexLoop)
                completeStepInformation(sequence_data, savedStepToModify.steps[stepIndexLoop], step)
                stepIndexLoop += 1 
            stepToModify = savedStepToModify  
        
        case "calc":
            # actionArray = [calcType, calcFloat, calcIncrement]
            stepToModify.type = actionArray[0]
            stepToModify.float= actionArray[1]
            stepToModify.increment = actionArray[2]
        
        case "init":
            # actionArray = [initGradients]
            stepToModify.gradients = actionArray[0]
        
        case "sync":
            # actionArray = [syncObject, syncTime]
            stepToModify.object = actionArray[0]
            if stepToModify.object not in sequence_data.objects:
                addObject(sequence_data=sequence_data, objectName=stepToModify.object)
            completeObjectInformation(sequence_data=sequence_data, objectName=stepToModify.object)
            stepToModify.time = actionArray[1]
        
        case "grad":
            # actionArray = [gradAxis, gradObject, gradTime, gradAmplitude, gradAmplidueOptions]
            stepToModify.axis = actionArray[0]
            stepToModify.object= actionArray[1]
            if stepToModify.object not in sequence_data.objects:
                addObject(sequence_data=sequence_data, objectName=stepToModify.object)
            completeObjectInformation(sequence_data=sequence_data, objectName=stepToModify.object)
            stepToModify.time = actionArray[2]
            if(actionArray[3]=="flip"):
                stepToModify.amplitude = "flip"
            elif(actionArray[3]=="equation"):
                # gradAmplidueOptions = [gradAmplType, gradAmplEquationName, gradAmplEquationValue]
                stepToModify.amplitude = Amplitude()
                stepToModify.amplitude.type = actionArray[4][0]
                stepToModify.amplitude.equation = actionArray[4][1]
                addEquation(sequence_data=sequence_data, equationName=stepToModify.amplitude.equation)
                sequence_data.equations[stepToModify.amplitude.equation].equation=actionArray[4][2]

        case "rf":
            # actionArray = [rfObject, rfTime, rfAddedPhaseType, rfAddedPhaseFloat]
            stepToModify.object= actionArray[0]
            if stepToModify.object not in sequence_data.objects:
                addObject(sequence_data=sequence_data, objectName=stepToModify.object)
            completeObjectInformation(sequence_data=sequence_data, objectName=stepToModify.object)
            stepToModify.time = actionArray[1]
            stepToModify.added_phase = AddedPhase()
            stepToModify.added_phase.type = actionArray[2]
            stepToModify.added_phase.float = actionArray[3]
        
        case "adc":
            # actionArray = [adcObject, adcTime, adcFrequency, adcPhase, adcAddedPhaseType, adcAddedPhaseFloat, adcMdh]
            stepToModify.object= actionArray[0]
            if stepToModify.object not in sequence_data.objects:
                addObject(sequence_data=sequence_data, objectName=stepToModify.object)
            completeObjectInformation(sequence_data=sequence_data, objectName=stepToModify.object)
            stepToModify.time = actionArray[1]
            stepToModify.frequency = actionArray[2]
            stepToModify.phase= actionArray[3]
            stepToModify.added_phase = AddedPhase()
            stepToModify.added_phase.type = actionArray[4]
            stepToModify.added_phase.float = actionArray[5]
            # TO DO !!! MDH -> adcMdh = actionArray[6]
        
        case "mark":
             # actionArray = [markTime]
            stepToModify.time = actionArray[0]
        
        case "submit":
            pass
        
        case _:
            print("The type " + actionInfo + " could not be identified.")


def completeObjectInformation(sequence_data, objectName, objectDuration, objectInfo):
    typeInfo = sequence_data.objects[objectName].type
    durationInfo = objectDuration
    match typeInfo:
        case "rf":
            # objectInfo = [rfArrayName, rfInitPhase, rfThickness, rfFlipAngle, rfPurpose]
            arrayInfo = objectInfo[0]
            addArray(sequence_data=sequence_data, arrayName=arrayInfo)
            if arrayInfo not in sequence_data.arrays:
                addArray(sequence_data=sequence_data, arrayName=arrayInfo)
            completeArrayInformation(sequence_data=sequence_data, arrayName=arrayInfo)
            sequence_data.objects[objectName]=RfExcitation( \
                duration = durationInfo, array = arrayInfo, \
                initial_phase =  objectInfo[1], thickness = objectInfo[2], \
                flipangle = objectInfo[3], purpose = objectInfo[4]) 
        
        case "grad":
            # objectInfo = [gradArray, gradTail, gradAmplitude]
            arrayInfo = objectInfo[0]
            addArray(sequence_data=sequence_data, arrayName=arrayInfo)
            if arrayInfo not in sequence_data.arrays:
                addArray(sequence_data=sequence_data, arrayName=arrayInfo)
            completeArrayInformation(sequence_data=sequence_data, arrayName=arrayInfo)
            sequence_data.objects[objectName]=GradientObject( \
                duration = durationInfo, array = arrayInfo,\
                tail = objectInfo[1], amplitude = objectInfo[2]) 
        
        case "adc":
            # objectInfo = [adcSamples, adcDwellTime]
            sequence_data.objects[objectName]=AdcReadout( \
                duration = durationInfo, samples = objectInfo[0], \
                dwelltime = objectInfo[1]) 
        
        case "sync":
            # objectInfo = [syncEvent]
            sequence_data.objects[objectName]=Ttl(duration = durationInfo, \
                                                  event = objectInfo[0]) 
        case _:
            print(U"The type " + typeInfo + " could not be identified.")


def completeArrayInformation(sequence_data, arrayName, arrayInfo):
    # arrayInfo = [arrayEncoding, arrayType, arraySize, arrayData]
    sequence_data.arrays[arrayName] = GradientTemplate(
                                    encoding = arrayInfo[0], type = arrayInfo[1], \
                                    size = arrayInfo[2], data = arrayInfo[3])


def completeEquationInformation(sequence_data, equationName, equationInfo):
    sequence_data.equations[equationName] = Equation(equation = equationInfo)
