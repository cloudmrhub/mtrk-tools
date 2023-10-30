################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################  

from SDL_read_write.pydanticSDLHandler import *

#############################################################
### User interface type connexion
#############################################################

# Allows to fill in parameters using console input in console mode and another 
# input in any other UI mode.
def inputParameter(UI_mode = "console", parameter = ""):
    if( UI_mode == "console"):
        return input()
    else:
        return parameter # TO DO: connect this to input from graphical UI

# Allows to print the console UI in console mode. May not be useful in any other
# UI mode.
def printIfConsole(UI_mode = "console", stringToPrint =""):
    if( UI_mode == "console"):
        print(stringToPrint)
    else:
        pass

# Setting of the current UI mode
UI_mode = "console"
# UI_mode = "other"

#############################################################
### User interface interaction
#############################################################

### Sections can be commented to play only the needed section(s)
def sdlFileCreator(sequence_data):
    sdlInitialize(sequence_data)

    # ### file section
    # printIfConsole(UI_mode = UI_mode, stringToPrint = "*************** - FILE - ***************")
    # printIfConsole(UI_mode = UI_mode, stringToPrint = "Do you want to provide file information? (yes/no)")
    # if(inputParameter(UI_mode=UI_mode) == "yes"):
    #     completeFileInformation(sequence_data)
    # else:
    #     printIfConsole(UI_mode = UI_mode, stringToPrint = "Default File information used.")
    
    # ### settings section
    # printIfConsole(UI_mode = UI_mode, stringToPrint = "*************** - SETTINGS - ***************")
    # printIfConsole(UI_mode = UI_mode, stringToPrint = "Do you want to provide general sequence settings? (yes/no)")
    # if(inputParameter(UI_mode=UI_mode) == "yes"):
    #     completeSequenceSettings(sequence_data)
    # else:
    #     printIfConsole(UI_mode = UI_mode, stringToPrint = "Default Settings information used.")

    # ### info section
    # printIfConsole(UI_mode = UI_mode, stringToPrint = "*************** - INFORMATION - ***************")
    # printIfConsole(UI_mode = UI_mode, stringToPrint = "Do you want to provide general sequence information? (yes/no)")
    # if(inputParameter(UI_mode=UI_mode) == "yes"):
    #     completeSequenceInformation(sequence_data)
    # else:
    #     printIfConsole(UI_mode = UI_mode, stringToPrint = "Default Info information used.")

    ### instructions section
    printIfConsole(UI_mode = UI_mode, stringToPrint = "*************** - INSTRUCTIONS - ***************")
    answer = "yes"
    while(answer == "yes"):
        printIfConsole(UI_mode = UI_mode, stringToPrint = "*** Do you want to add a new instruction? (yes/no)")
        answer = inputParameter(UI_mode=UI_mode)
        if(answer == "yes"):
            printIfConsole(UI_mode = UI_mode, stringToPrint = "Instruction name (str):")
            instructionName = inputParameter(UI_mode=UI_mode)
            addInstruction(sequence_data, instructionName)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "Do you want to provide instruction information? (yes/no)")
            if(inputParameter(UI_mode=UI_mode) == "yes"):
                completeInstructionInformation(sequence_data.instructions[instructionName])
                print("instructionToModify = "+str(sequence_data.instructions[instructionName]))
            else:
                printIfConsole(UI_mode = UI_mode, stringToPrint = "Default Instruction information used.")
        else:
            printIfConsole(UI_mode = UI_mode, stringToPrint = "*******************************************")

    # ### objects section
    # printIfConsole(UI_mode = UI_mode, stringToPrint = "*************** - OBJECTS - ***************")
    # answer = "yes"
    # while(answer == "yes"):
    #     printIfConsole(UI_mode = UI_mode, stringToPrint = "*** Do you want to add a new object? (yes/no)")
    #     answer = inputParameter(UI_mode=UI_mode)
    #     if(answer == "yes"):
    #         printIfConsole(UI_mode = UI_mode, stringToPrint = "Object name (str):")
    #         objectName = inputParameter(UI_mode=UI_mode)
    #         addObject(sequence_data, objectName)
    #         printIfConsole(UI_mode = UI_mode, stringToPrint = "Do you want to provide object information? (yes/no)")
    #         if(inputParameter(UI_mode=UI_mode) == "yes"):
    #             completeObjectInformation(sequence_data, objectName)
    #         else:
    #             printIfConsole(UI_mode = UI_mode, stringToPrint = "Default Object information used.")
    #     else:
    #         printIfConsole(UI_mode = UI_mode, stringToPrint = "*******************************************")
    
    # ### arrays section
    # printIfConsole(UI_mode = UI_mode, stringToPrint = "*************** - ARRAYS - ***************")
    # answer = "yes"
    # while(answer == "yes"):
    #     printIfConsole(UI_mode = UI_mode, stringToPrint = "*** Do you want to add a new array? (yes/no)")
    #     answer = inputParameter(UI_mode=UI_mode)
    #     if(answer == "yes"):
    #         printIfConsole(UI_mode = UI_mode, stringToPrint = "Array name (str):")
    #         arrayName = inputParameter(UI_mode=UI_mode)
    #         addArray(sequence_data, arrayName)
    #         printIfConsole(UI_mode = UI_mode, stringToPrint = "Do you want to provide array information? (yes/no)")
    #         if(inputParameter(UI_mode=UI_mode) == "yes"):
    #             completeArrayInformation(sequence_data, arrayName)
    #         else:
    #             printIfConsole(UI_mode = UI_mode, stringToPrint = "Default Array information used.")
    #     else:
    #         printIfConsole(UI_mode = UI_mode, stringToPrint = "*******************************************")

    # ### equations section
    # printIfConsole(UI_mode = UI_mode, stringToPrint = "*************** - EQUATIONS - ***************")
    # answer = "yes"
    # while(answer == "yes"):
    #     printIfConsole(UI_mode = UI_mode, stringToPrint = "*** Do you want to add a new equation? (yes/no)")
    #     answer = inputParameter(UI_mode=UI_mode)
    #     if(answer == "yes"):
    #         printIfConsole(UI_mode = UI_mode, stringToPrint = "Equation name (str):")
    #         equationName = inputParameter(UI_mode=UI_mode)
    #         addEquation(sequence_data, equationName)
    #         printIfConsole(UI_mode = UI_mode, stringToPrint = "Do you want to provide equation information? (yes/no)")
    #         if(inputParameter(UI_mode=UI_mode) == "yes"):
    #             completeEquationInformation(sequence_data, \
    #                                                         equationName)
    #         else:
    #             printIfConsole(UI_mode = UI_mode, stringToPrint = "Default Equation information used.")
    #     else:
    #         printIfConsole(UI_mode = UI_mode, stringToPrint = "*******************************************")
    
    return sequence_data


#############################################################
### Functions to create SDL file objects
#############################################################

# TO DO: automatically create linked objects when they do not already exist:
# Block -> creation of a new instruction
# Object -> creation of a new object
# Equation -> creation of a new equation
# Array -> creation of a new array

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


def addStep(instructionToModify, stepIndex):
    printIfConsole(UI_mode = UI_mode, stringToPrint = "Provide step action type: ")
    printIfConsole(UI_mode = UI_mode, stringToPrint = "Action (run_block/loop/calc/init/sync/grad/rf/adc/mark/submit): ")
    actionName = inputParameter(UI_mode=UI_mode)
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
            mdhOptAnswer = "yes"
            while(mdhOptAnswer == "yes"):
                printIfConsole(UI_mode = UI_mode, stringToPrint = "Do you want to add a new MDH option? (yes/no)")
                mdhOptAnswer = inputParameter(UI_mode=UI_mode)
                if(mdhOptAnswer == "yes"):
                    addMdhOption(instructionToModify.steps, stepIndex)
                else:
                    pass
        case "mark":
            instructionToModify.steps.append(Mark())
        case "submit":
            instructionToModify.steps.append(Submit())
        case _: 
            printIfConsole(UI_mode = UI_mode, stringToPrint = actionName + " is not available")    


def addMdhOption(stepToModify, stepIndex):
    printIfConsole(UI_mode = UI_mode, stringToPrint = "Provide MDH option information: ")
    printIfConsole(UI_mode = UI_mode, stringToPrint = "MDH option type (str): ")
    stepToModify[stepIndex].mdh[inputParameter(UI_mode=UI_mode)] = MdhOption()


def addObject(sequence_data, objectName):
    printIfConsole(UI_mode = UI_mode, stringToPrint = "Object type (rf/grad/adc/sync):")
    typeName = inputParameter(UI_mode=UI_mode)
    match typeName:
        case "rf":
           sequence_data.objects[objectName]=RfExcitation() 
        case "grad":
            sequence_data.objects[objectName]=GradientObject() 
        case "adc":
            sequence_data.objects[objectName]=AdcReadout() 
        case "sync":
            sequence_data.objects[objectName]=Ttl() 
        case _:
            printIfConsole(UI_mode = UI_mode, stringToPrint = typeName + " is not available")


def addArray(sequence_data, arrayName):
    sequence_data.arrays[arrayName] = GradientTemplate()


def addEquation(sequence_data, equationName):
    sequence_data.equations[equationName] = Equation()


#############################################################
### Functions to fill SDL file objects with new values
#############################################################

def completeFileInformation(sequence_data):
    printIfConsole(UI_mode = UI_mode, stringToPrint = "format (str)")
    formatInfo = inputParameter(UI_mode=UI_mode)
    printIfConsole(UI_mode = UI_mode, stringToPrint = "version (int)")
    versionInfo = int(inputParameter(UI_mode=UI_mode))
    printIfConsole(UI_mode = UI_mode, stringToPrint = "measurement (str)")
    measurementInfo = inputParameter(UI_mode=UI_mode)
    printIfConsole(UI_mode = UI_mode, stringToPrint = "system (str)")
    systemInfo = inputParameter(UI_mode=UI_mode)
    sequence_data.file = File(format = formatInfo, version = versionInfo, \
                             measurement = measurementInfo, system = systemInfo)

def completeSequenceSettings(sequence_data):
    printIfConsole(UI_mode = UI_mode, stringToPrint = "readout_os (int)")
    readoutOsInfo = inputParameter(UI_mode=UI_mode)
    sequence_data.settings = Settings(readout_os = readoutOsInfo)
    
def completeSequenceInformation(sequence_data):
    printIfConsole(UI_mode = UI_mode, stringToPrint = "description (str)")
    descriptionInfo = inputParameter(UI_mode=UI_mode)
    printIfConsole(UI_mode = UI_mode, stringToPrint = "slices (int)")
    slicesInfo = int(inputParameter(UI_mode=UI_mode))
    printIfConsole(UI_mode = UI_mode, stringToPrint = "fov (int)")
    fovInfo = int(inputParameter(UI_mode=UI_mode))
    printIfConsole(UI_mode = UI_mode, stringToPrint = "pelines (int)")
    pelinesInfo = int(inputParameter(UI_mode=UI_mode))
    printIfConsole(UI_mode = UI_mode, stringToPrint = "seqstring (str)")
    seqstringInfo = inputParameter(UI_mode=UI_mode)
    printIfConsole(UI_mode = UI_mode, stringToPrint = "reconstruction (str)")
    reconstructionInfo = inputParameter(UI_mode=UI_mode)
    sequence_data.infos = Info(description = descriptionInfo, \
                               slices = slicesInfo, fov = fovInfo,  \
                               pelines = pelinesInfo, seqstring = seqstringInfo,\
                               reconstruction = reconstructionInfo)

def completeInstructionInformation(instructionToModify):
    printIfConsole(UI_mode = UI_mode, stringToPrint = "Message to print (str): ")
    instructionToModify.print_message = inputParameter(UI_mode=UI_mode)
    printIfConsole(UI_mode = UI_mode, stringToPrint = "Printing counter option (on/off): ")
    printCounterOption = inputParameter(UI_mode=UI_mode)
    if(printCounterOption=="on" or printCounterOption=="off"):
        instructionToModify.print_counter = printCounterOption
    else:
        printIfConsole(UI_mode = UI_mode, stringToPrint = printCounterOption + " is not valid.")
    stepAnswer = "yes"
    stepIndex = 0
    while(stepAnswer == "yes"):
        printIfConsole(UI_mode = UI_mode, stringToPrint = "Do you want to add a new step? (yes/no)")
        stepAnswer = inputParameter(UI_mode=UI_mode)
        if(stepAnswer == "yes"):
            addStep(instructionToModify, stepIndex)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "Do you want to provide step information? (yes/no)")
            if(inputParameter(UI_mode=UI_mode) == "yes"):
                stepToModify = instructionToModify.steps[stepIndex]
                completeStepInformation(stepToModify, "Instruction")
            else:
                printIfConsole(UI_mode = UI_mode, stringToPrint = "Default Instruction information used.")
            stepIndex += 1
        else:
            pass

def completeStepInformation(stepToModify, instructionOrLoop):
    printIfConsole(UI_mode = UI_mode, stringToPrint = "Completing for step in " + instructionOrLoop)
    actionInfo = stepToModify.action
    printIfConsole(UI_mode = UI_mode, stringToPrint = "Provide information for step of type " + str(actionInfo) + ": ")
    match actionInfo:
        case "run_block":
            printIfConsole(UI_mode = UI_mode, stringToPrint = "block (str)")
            stepToModify.block= inputParameter(UI_mode=UI_mode)
        case "loop":
            savedStepToModify = stepToModify
            printIfConsole(UI_mode = UI_mode, stringToPrint = "counter (int)")
            savedStepToModify.counter = inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "range (int)")
            savedStepToModify.range= inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "steps (Step)")
            stepAnswerLoop = "yes"
            stepIndexLoop = 0
            while(stepAnswerLoop == "yes"):
                printIfConsole(UI_mode = UI_mode, stringToPrint = "Do you want to add a new step in the loop? (yes/no)")
                stepAnswerLoop = inputParameter(UI_mode=UI_mode)
                nextAnswer = "yes"
                if(stepAnswerLoop == "yes"):
                    addStep(savedStepToModify, stepIndexLoop)
                    printIfConsole(UI_mode = UI_mode, stringToPrint = "Do you want to provide step information? (yes/no)")
                    nextAnswer = inputParameter(UI_mode=UI_mode)
                    if(nextAnswer == "yes"):
                        completeStepInformation(savedStepToModify.steps[stepIndexLoop], "Loop")
                    else:
                        printIfConsole(UI_mode = UI_mode, stringToPrint = "Default Loop information used.")
                    stepIndexLoop += 1
                else:
                    pass  
            print(savedStepToModify)  
            stepToModify = savedStepToModify  
        case "calc":
            printIfConsole(UI_mode = UI_mode, stringToPrint = "type (str)")
            stepToModify.type = inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "float (float)")
            stepToModify.float= inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "increment (int)")
            stepToModify.increment = inputParameter(UI_mode=UI_mode) 
        case "init":
            printIfConsole(UI_mode = UI_mode, stringToPrint = "gradients (str)")
            stepToModify.gradients = inputParameter(UI_mode=UI_mode)
        case "sync":
            printIfConsole(UI_mode = UI_mode, stringToPrint = "object (str)")
            stepToModify.object = inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "time (int)")
            stepToModify.time = inputParameter(UI_mode=UI_mode)
        case "grad":
            printIfConsole(UI_mode = UI_mode, stringToPrint = "axis (str -> precise!)")
            stepToModify.axis = inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "object (str)")
            stepToModify.object= inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "time (int)")
            stepToModify.time = inputParameter(UI_mode=UI_mode) 
        case "rf":
            printIfConsole(UI_mode = UI_mode, stringToPrint = "object (str)")
            stepToModify.object= inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "time (float)")
            stepToModify.time = inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "added_phase (AddedPhase)")
            printIfConsole(UI_mode = UI_mode, stringToPrint = "passed for now")
        case "adc":
            printIfConsole(UI_mode = UI_mode, stringToPrint = "object (str)")
            stepToModify.object= inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "time (float)")
            stepToModify.time = inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "frequency (int)")
            stepToModify.frequency = inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "phase (int)")
            stepToModify.phase= inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "added_phase (AddedPhase)")
            printIfConsole(UI_mode = UI_mode, stringToPrint = "passed for now")
            printIfConsole(UI_mode = UI_mode, stringToPrint = "mdh (dict[str, MdhOption])")
            printIfConsole(UI_mode = UI_mode, stringToPrint = "passed for now") 
        case "mark":
            printIfConsole(UI_mode = UI_mode, stringToPrint = "time (float)")
            stepToModify.time = inputParameter(UI_mode=UI_mode)
        case "submit":
            printIfConsole(UI_mode = UI_mode, stringToPrint = "Nothing to customize in submit.")
        case _:
            printIfConsole(UI_mode = UI_mode, stringToPrint = "The type " + actionInfo + " could not be identified.")


def completeObjectInformation(sequence_data, objectName):
    typeInfo = sequence_data.objects[objectName].type
    printIfConsole(UI_mode = UI_mode, stringToPrint = "Provide information for object of type " + str(typeInfo) + ": ")
    printIfConsole(UI_mode = UI_mode, stringToPrint = "duration (int)")
    durationInfo = inputParameter(UI_mode=UI_mode)
    match typeInfo:
        case "rf":
           printIfConsole(UI_mode = UI_mode, stringToPrint = "array (str)")
           arrayInfo = inputParameter(UI_mode=UI_mode)
           printIfConsole(UI_mode = UI_mode, stringToPrint = "initial_phase (int)")
           initPhaseInfo = inputParameter(UI_mode=UI_mode)
           printIfConsole(UI_mode = UI_mode, stringToPrint = "thickness (int)")
           thicknessInfo = inputParameter(UI_mode=UI_mode)
           printIfConsole(UI_mode = UI_mode, stringToPrint = "flipangle (int)")
           flipangleInfo = inputParameter(UI_mode=UI_mode)
           printIfConsole(UI_mode = UI_mode, stringToPrint = "purpose (str)")
           purposeInfo = inputParameter(UI_mode=UI_mode)
           sequence_data.objects[objectName]=RfExcitation( \
               duration = durationInfo, array = arrayInfo, \
               initial_phase =  initPhaseInfo, thickness = thicknessInfo, \
               flipangle = flipangleInfo, purpose = purposeInfo) 
        case "grad":
            printIfConsole(UI_mode = UI_mode, stringToPrint = "array (str)")
            arrayInfo = inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "tail (int)")
            tailInfo = inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "amplitude (float)")
            amplitudeInfo = inputParameter(UI_mode=UI_mode)
            sequence_data.objects[objectName]=GradientObject( \
                duration = durationInfo, array = arrayInfo,\
                tail = tailInfo, amplitude = amplitudeInfo) 
        case "adc":
            printIfConsole(UI_mode = UI_mode, stringToPrint = "samples (int)")
            samplesInfo = inputParameter(UI_mode=UI_mode)
            printIfConsole(UI_mode = UI_mode, stringToPrint = "dwelltime (int)")
            dwelltimeInfo = inputParameter(UI_mode=UI_mode)
            sequence_data.objects[objectName]=AdcReadout( \
                duration = durationInfo, samples = samplesInfo, \
                dwelltime = dwelltimeInfo) 
        case "sync":
            printIfConsole(UI_mode = UI_mode, stringToPrint = "event (str)")
            eventInfo = inputParameter(UI_mode=UI_mode)
            sequence_data.objects[objectName]=Ttl(duration = durationInfo, \
                                                  event = eventInfo) 
        case _:
            printIfConsole(UI_mode = UI_mode, stringToPrint = "The type " + typeInfo + " could not be identified.")


def completeArrayInformation(sequence_data, arrayName):
    printIfConsole(UI_mode = UI_mode, stringToPrint = "encoding (str)")
    encodingInfo = inputParameter(UI_mode=UI_mode)
    printIfConsole(UI_mode = UI_mode, stringToPrint = "type (str)")
    typeInfo = inputParameter(UI_mode=UI_mode)
    printIfConsole(UI_mode = UI_mode, stringToPrint = "size (int)")
    sizeInfo = int(inputParameter(UI_mode=UI_mode))
    printIfConsole(UI_mode = UI_mode, stringToPrint = "data (float, float, ...)")
    dataInfo = [float(elem) for elem in inputParameter(UI_mode=UI_mode).split(", ")]
    sequence_data.arrays[arrayName] = GradientTemplate(
                                     encoding = encodingInfo, type = typeInfo, \
                                     size = sizeInfo, data = dataInfo)


def completeEquationInformation(sequence_data, equationName):
    printIfConsole(UI_mode = UI_mode, stringToPrint = "equation (str)")
    equationInfo = inputParameter(UI_mode=UI_mode)
    sequence_data.equations[equationName] = Equation(equation = equationInfo)
