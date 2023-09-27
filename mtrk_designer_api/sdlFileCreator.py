################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################  

from SDL_read_write.pydanticSDLHandler import *

#############################################################
### Console user interface
#############################################################

def sdlFileCreator(sequence_data):
    sdlInitialize(sequence_data)

    ### file section
    print("*************** - FILE - ***************")
    print("Do you want to provide file information? (yes/no)")
    if(input() == "yes"):
        sequence_data = completeFileInformation(sequence_data)
    else:
        print("Default File information used.")

    ### info section
    print("*************** - INFORMATION - ***************")
    print("Do you want to provide general sequence information? (yes/no)")
    if(input() == "yes"):
        sequence_data = completeSequenceInformation(sequence_data)
    else:
        print("Default Info information used.")

    ### settings section
    sequence_data.settings = Settings()

    ### instructions section
    print("*************** - INSTRUCTIONS - ***************")
    answer = "yes"
    while(answer == "yes"):
        print("*** Do you want to add a new instruction? (yes/no)")
        answer = input()
        if(answer == "yes"):
            sequence_data = addInstruction(sequence_data)
        else:
            print("*******************************************")

    ### objects section
    print("*************** - OBJECTS - ***************")
    answer = "yes"
    while(answer == "yes"):
        print("*** Do you want to add a new object? (yes/no)")
        answer = input()
        if(answer == "yes"):
            sequence_data = addObject(sequence_data)
        else:
            print("*******************************************")
    
    ### arrays section
    print("*************** - ARRAYS - ***************")
    answer = "yes"
    while(answer == "yes"):
        print("*** Do you want to add a new array? (yes/no)")
        answer = input()
        if(answer == "yes"):
            print("Array name (str):")
            arrayName = input()
            sequence_data = addArray(sequence_data, arrayName)
            print("Do you want to provide array information? (yes/no)")
            if(input() == "yes"):
                sequence_data = completeArrayInformation(sequence_data, \
                                                         arrayName)
            else:
                print("Default Array information used.")
        else:
            print("*******************************************")

    ### equations section
    print("*************** - EQUATIONS - ***************")
    answer = "yes"
    while(answer == "yes"):
        print("*** Do you want to add a new equation? (yes/no)")
        answer = input()
        if(answer == "yes"):
            print("Equation name (str):")
            equationName = input()
            sequence_data = addEquation(sequence_data, equationName)
            print("Do you want to provide equation information? (yes/no)")
            if(input() == "yes"):
                sequence_data = completeEquationInformation(sequence_data, \
                                                            equationName)
            else:
                print("Default Equation information used.")
        else:
            print("*******************************************")
    
    return sequence_data


#############################################################
### Functions to create SDL file objects
#############################################################

def sdlInitialize(sequence_data):
    ### SDL file initialization
    sequence_data.file = File()
    sequence_data.infos = Info()
    sequence_data.settings = Settings()
    sequence_data.instructions = {}
    sequence_data.objects = {}
    sequence_data.arrays = {}
    sequence_data.equations = {}
    return sequence_data


def addInstruction(sequence_data):
    print("Provide instruction information: ")
    print("Instruction name (str): ")
    instructionName = input()
    sequence_data.instructions[instructionName] = Instruction(steps=[])
    print("Message to print (str): ")
    sequence_data.instructions[instructionName].print_message = input()
    print("Printing counter option (on/off): ")
    printCounterOption = input()
    if(printCounterOption=="on" or printCounterOption=="off"):
        sequence_data.instructions[instructionName].print_counter = \
                                                              printCounterOption
    else:
        print(printCounterOption + " is not valid.")
    stepAnswer = "yes"
    stepIndex = 0
    while(stepAnswer == "yes"):
        print("Do you want to add a new step? (yes/no)")
        stepAnswer = input()
        if(stepAnswer == "yes"):
            sequence_data = addStep(sequence_data, instructionName, stepIndex)
            stepIndex += 1
        else:
            pass
        
    return sequence_data

def addStep(sequence_data, instructionName, stepIndex):
    print("Provide step information: ")
    print("Action (calc/init/sync/grad/rf/adc/mark/submit): ")
    actionName = input()
    match actionName:
        case "calc":
            sequence_data.instructions[instructionName].steps.append(Calc())
        case "init":
            sequence_data.instructions[instructionName].steps.append(Init())
        case "sync":
            sequence_data.instructions[instructionName].steps.append(Sync())
        case "grad":
            sequence_data.instructions[instructionName].steps.append(Grad())
        case "rf":
            sequence_data.instructions[instructionName].steps.append( \
                                                 Rf(added_phase = AddedPhase()))
        case "adc":
            sequence_data.instructions[instructionName].steps.append( \
                                        Adc(added_phase = AddedPhase(), mdh={}))
            mdhOptAnswer = "yes"
            while(mdhOptAnswer == "yes"):
                print("Do you want to add a new MDH option? (yes/no)")
                mdhOptAnswer = input()
                if(mdhOptAnswer == "yes"):
                    sequence_data = addMdhOption(sequence_data,\
                                                 instructionName, stepIndex)
                else:
                    pass
        case "mark":
            sequence_data.instructions[instructionName].steps.append(Mark())
        case "submit":
            sequence_data.instructions[instructionName].steps.append(Submit())
        case _: 
            print(actionName + " is not available")    
    return sequence_data

def addMdhOption(sequence_data, instructionName, stepIndex):
    print("Provide MDH option information: ")
    print("MDH option type (str): ")
    sequence_data.instructions[instructionName].steps[stepIndex].mdh[input()]=\
                                                                     MdhOption()
    return sequence_data

def addObject(sequence_data):
    print("Provide object information: ")
    print("Object name (str): ")
    objectName = input()
    # sequence_data.objects[objectName] = Object()
    print("Object type (rf/grad/adc/sync):")
    typeName = input()
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
            print(typeName + "is not available")
    return sequence_data

def addArray(sequence_data, arrayName):
    sequence_data.arrays[arrayName] = GradientTemplate()
    return sequence_data

def addEquation(sequence_data, equationName):
    sequence_data.equations[equationName] = Equation()
    return sequence_data

#############################################################
### Functions to fill SDL file objects with new values
#############################################################

def completeFileInformation(sequence_data):
    print("format (str)")
    formatInfo = input()
    print("version (int)")
    versionInfo = int(input())
    print("measurement (str)")
    measurementInfo = input()
    print("system (str)")
    systemInfo = input()
    sequence_data.file = File(format = formatInfo, version = versionInfo, \
                             measurement = measurementInfo, system = systemInfo)
    return sequence_data
    
def completeSequenceInformation(sequence_data):
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
    sequence_data.infos = Info(description = descriptionInfo, \
                               slices = slicesInfo, fov = fovInfo,  \
                               pelines = pelinesInfo, seqstring = seqstringInfo,\
                               reconstruction = reconstructionInfo)
    return sequence_data

def completeArrayInformation(sequence_data, arrayName):
    print("encoding (str)")
    encodingInfo = input()
    print("type (str)")
    typeInfo = input()
    print("size (int)")
    sizeInfo = int(input())
    print("data (float, float, ...)")
    dataInfo = [float(elem) for elem in input().split(", ")]
    sequence_data.arrays[arrayName] = GradientTemplate(
                                     encoding = encodingInfo, type = typeInfo, \
                                     size = sizeInfo, data = dataInfo)
    return sequence_data

def completeEquationInformation(sequence_data, equationName):
    print("equation (str)")
    equationInfo = input()
    sequence_data.equations[equationName] = Equation(equation = equationInfo)
    return sequence_data