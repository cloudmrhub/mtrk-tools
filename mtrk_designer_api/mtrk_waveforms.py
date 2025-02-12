import mtrkPulpy as mpp
import matplotlib.pyplot as plt
from SDL_read_write.pydanticSDLHandler import *

# fov (float): imaging field of view in cm.
# n (int): # of pixels (square). N = etl*nl, where etl = echo-train-len
#     and nl = # leaves (shots). nl default 1.
# etl (int): echo train length.
# dt (float): sample time in s.
# gamp (float): max gradient amplitude in mT/m.
# gslew (float): max slew rate in mT/m/ms.
# offset (int): used for multi-shot EPI goes from 0 to #shots-1
# dirx (int): x direction of EPI -1 left to right, 1 right to left
# diry (int): y direction of EPI -1 bottom-top, 1 top-bottom

def add_epi_train(base_sequence, start_time, n, etl, gamp, gslew, offset=0, dirx=-1, diry=1):
    # base_sequence.instructions = {}

    fov = round(base_sequence.infos.fov * 1e-4, 6)  # Is the FOV in the right unit now?
    dt = 1e-5

    ## Creating a main loop
    epiLoop = Loop(counter = 2, range = 1, 
                    steps = [])
    base_sequence.instructions.update({"block_epi" : {}})
    base_sequence.instructions["block_epi"].update(epiLoop)

    blocks = mpp.mtrk_epi(fov, start_time, n, etl, dt, gamp, gslew, offset, dirx, diry)

    ## Looping over blocks
    for block_index in range(0, len(blocks)):
        ## Creating loops (only if the iteration number is greater than 1)
        loop_iterations = blocks[block_index][0]
        block_startTime = int(blocks[block_index][1]*1e5)
        block = Instruction(print_counter = "on",
                            print_message = "Running block " + str(block_index),
                            time = block_startTime,
                            steps = [])
        base_sequence.instructions.update({"block_" + str(block_index) : {}})
        base_sequence.instructions["block_" + str(block_index)].update(block)
        if loop_iterations > 1:
            loop = Loop(counter = block_index, 
                        range = loop_iterations, 
                        steps = [Step(action = "run_block", 
                                      block = "block_" + str(block_index))])
            base_sequence.instructions["block_epi"]["steps"].append(loop)
        else:
            base_sequence.instructions["block_epi"]["steps"].append(Step(action = "run_block", 
                                                                 block = "block_" + str(block_index)))

        ## Looping over block instructions
        for index in range(2, len(blocks[block_index])):
            ## Combined index to identify instructions, objects and arrays
            combined_index = str(block_index) + "_" + str(index)

            ## Creating gradient events, along with their respective arrays and objects
            if blocks[block_index][index][2] == "read" or blocks[block_index][index][2] == "slice" or blocks[block_index][index][2] == "phase":
                ## Creating gradient arrays
                grad_array = GradientTemplate(encoding = "text", 
                                              type = "float",
                                              size = blocks[block_index][index][1],
                                              data = blocks[block_index][index][0])
                ## Checking if the array already exists in the arrays section
                if dict(grad_array) in base_sequence.arrays.values():
                    array_name = [key for key, value in base_sequence.arrays.items() if value == dict(grad_array)][0] 
                else:
                    array_name = "grad_array_" + combined_index
                    base_sequence.arrays.update({array_name: {}})
                    base_sequence.arrays[array_name].update(grad_array)

                ## Creating gradient objects
                grad_object = GradientObject(duration = blocks[block_index][index][1] * 10, 
                                             array = array_name, 
                                             tail = 0, 
                                             amplitude = blocks[block_index][index][3])
                ## Checking if the gradient already exists in the gradients section
                if dict(grad_object) in base_sequence.objects.values():
                    object_name = [key for key, value in base_sequence.objects.items() if value == dict(grad_object)][0] 
                else:
                    object_name = "grad_object_" + combined_index
                    base_sequence.objects.update({object_name: {}})
                    base_sequence.objects[object_name].update(grad_object)

                ## Creating gradient instructions
                gradient = Grad(axis = blocks[block_index][index][2], 
                                object = object_name, 
                                time = int(blocks[block_index][index][4]*1e5))
                base_sequence.instructions["block_" + str(block_index)]["steps"].append(gradient)

            ## Creating ADC events, along with their respective objects       
            elif blocks[block_index][index][2] == "adc":
                ## Creating ADC objects
                adc_object = AdcReadout(duration = blocks[block_index][index][1]*10, 
                                        samples = blocks[block_index][index][1], 
                                        dwelltime = 30000)

                ## Checking if the ADC object already exists in the objects section
                if dict(adc_object) in base_sequence.objects.values():
                    object_name = [key for key, value in base_sequence.objects.items() if value == dict(adc_object)][0] 
                else:
                    object_name = "adc_object_" + combined_index
                    base_sequence.objects.update({object_name: {}})
                    base_sequence.objects[object_name].update(adc_object)

                ## Creating ADC instructions
                mdhOptionsDict = { "line": MdhOption(type = "counter", counter = block_index), 
                                   "first_scan_slice": MdhOption(type = "counter", counter = block_index, target = 0),
                                   "last_scan_slice": MdhOption(type = "counter", counter = block_index, target = loop_iterations-1)}
                adc = Adc(object = object_name, 
                          time = int(blocks[block_index][index][4]*1e5), 
                          frequency = 0, 
                          phase = 0, 
                          added_phase = AddedPhase(type = "float", 
                                                   float = 0.0), 
                          mdh = mdhOptionsDict)
                base_sequence.instructions["block_" + str(block_index)]["steps"].append(adc)
    
    return base_sequence


    # subplot, axis = plt.subplots(2, sharex=True)
    # subplot.suptitle("EPI trajectory")
    # axis[0].set_title("gy")
    # axis[0].set_ylim(ymin=-20, ymax=20)
    # axis[0].plot(gy, label='gy')
    # axis[1].set_title("gx")
    # axis[1].set_ylim(ymin=-20, ymax=20)
    # axis[1].plot(gx, label='gx')
    # plt.show()