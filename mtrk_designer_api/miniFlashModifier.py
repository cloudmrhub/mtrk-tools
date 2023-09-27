################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################  

from SDL_read_write.pydanticSDLHandler import *

def miniFlashModifier(mainLoop, PELoop, \
                      sequence_data, fileInit, infoInit, settingsInit, \
                      rfSpoiling, initialization, synchronization, rfPulse, \
                      sliceSelectionGradient, sliceRefocusingGradient, \
                      readoutDephasingGradient, phaseEncodingGradient, \
                      readoutGradient, sliceSpoilingGradient, \
                      phaseSpoilingGradient, analogToDigitalConverter, \
                      marking, submit, rfExcitation, gradientList, adcReadout, \
                      ttl, arrayList, equationList):
    # temporarily relying on classes to discriminate between spoiling and other gradients
    
    ### file section
    sequence_data.file = fileInit

    ### info section
    sequence_data.infos = infoInit

    ### settings section
    sequence_data.settings = settingsInit

    ### instructions section
    for instruction in list(sequence_data.instructions):
        for data in sequence_data.instructions[instruction]:
            if data[0] == "steps":
                counter = 0
                for counter in range(len(data[1])):
                    elem = \
                          sequence_data.instructions[instruction].steps[counter]
                    if type(elem) == Calc:
                        sequence_data.instructions[instruction].steps[counter] \
                                                                    = rfSpoiling
                    elif type(elem) == Init:
                        sequence_data.instructions[instruction].steps[counter] \
                                                                = initialization
                    elif type(elem) == Sync:
                        sequence_data.instructions[instruction].steps[counter] \
                                                               = synchronization
                    elif type(elem) == Rf:
                        sequence_data.instructions[instruction].steps[counter] \
                                                                       = rfPulse
                    elif type(elem) == Grad:
                        if elem.object == "grad_slice_select":
                            sequence_data.instructions[instruction].steps[counter] \
                                                        = sliceSelectionGradient
                        if elem.object == "grad_slice_refocus":
                            sequence_data.instructions[instruction].steps[counter] \
                                                       = sliceRefocusingGradient
                        if elem.object == "grad_read_dephase":
                            sequence_data.instructions[instruction].steps[counter] \
                                                      = readoutDephasingGradient
                        if elem.object == "grad_phase_encode":
                            sequence_data.instructions[instruction].steps[counter] \
                                                         = phaseEncodingGradient
                        if elem.object == "grad_read_readout":
                            sequence_data.instructions[instruction].steps[counter] \
                                                               = readoutGradient
                    elif type(elem) == GradWithAmplitude:
                        if elem.object == "grad_slice_refocus":
                            sequence_data.instructions[instruction].steps[counter] \
                                                         = sliceSpoilingGradient
                        elif elem.object == "grad_phase_encode" and \
                                                       elem.amplitude == "flip":
                            sequence_data.instructions[instruction].steps[counter] \
                                                         = phaseSpoilingGradient
                        elif elem.object == "grad_phase_encode":
                            sequence_data.instructions[instruction].steps[counter] \
                                                         = phaseEncodingGradient
                    elif type(elem) == Grad:
                        if elem.object == "grad_slice_select":
                            sequence_data.instructions[instruction].steps[counter] \
                                                        = sliceSelectionGradient
                        if elem.object == "grad_slice_refocus":
                            sequence_data.instructions[instruction].steps[counter] \
                                                       = sliceRefocusingGradient
                        if elem.object == "grad_read_dephase":
                            sequence_data.instructions[instruction].steps[counter] \
                                                      = readoutDephasingGradient
                        if elem.object == "grad_phase_encode":
                            sequence_data.instructions[instruction].steps[counter] \
                                                         = phaseEncodingGradient
                        if elem.object == "grad_read_readout":
                            sequence_data.instructions[instruction].steps[counter] \
                                                               = readoutGradient
                    elif type(elem) == Adc:
                        sequence_data.instructions[instruction].steps[counter] \
                                                      = analogToDigitalConverter
                    elif type(elem) == Mark:
                        sequence_data.instructions[instruction].steps[counter] \
                                                                       = marking
                    elif type(elem) == Submit:
                        sequence_data.instructions[instruction].steps[counter] \
                                                                        = submit
                    elif type(elem) == Loop:
                        if elem.steps[0].block == "block_phaseEncoding":
                            sequence_data.instructions[instruction].steps[counter] \
                                                                      = mainLoop  
                        else:
                            sequence_data.instructions[instruction].steps[counter] \
                                                                      = PELoop   
                    else:
                        print("error " + str(elem))

    ### objects section
    gradient_counter = 0
    for object in list(sequence_data.objects):
        if list(sequence_data.objects[object])[0][1] == "rf":
            sequence_data.objects[object] = rfExcitation
        if list(sequence_data.objects[object])[0][1] == "grad":
            sequence_data.objects[object] = gradientList[gradient_counter]
            gradient_counter += 1
        if list(sequence_data.objects[object])[0][1] == "adc":
            sequence_data.objects[object] = adcReadout
        if list(sequence_data.objects[object])[0][1] == "sync":
            sequence_data.objects[object] = ttl
    
    ### arrays section
    array_counter = 0
    for array in list(sequence_data.arrays):
        sequence_data.arrays[array] = arrayList[array_counter]
        array_counter += 1

    ### equations section
    equation_counter = 0
    for equation in list(sequence_data.equations):
        sequence_data.equations[equation] = equationList[equation_counter]
        equation_counter += 1

    return sequence_data