################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################  

from steps.Gradient import Gradient
from SDL_read_write.pydanticSDLHandler import *

def miniFlashModifier(sequence_data, fileInit, infoInit, settingsInit, \
                      initialization, synchronization, rfPulse, \
                      sliceSelectionGradient, sliceRefocusingGradient, \
                      readoutDephasingGradient, phaseEncodingGradient, \
                      readoutGradient, sliceSpoilingGradient, \
                      phaseSpoilingGradient, analogToDigitalConverter, \
                      marking, submit, rfExcitation, gradientList, adcReadout, \
                      ttl):
    # temporarily relying on classes to discriminate between spoiling and other gradients
    sequence_data.file.format = fileInit.getFormat()
    sequence_data.file.version = fileInit.getVersion()
    sequence_data.file.measurement = fileInit.getMeasurement()
    sequence_data.file.system = fileInit.getSystem()

    sequence_data.infos.description = infoInit.getDescription()
    sequence_data.infos.slices = infoInit.getSlices()
    sequence_data.infos.fov = infoInit.getFov()
    sequence_data.infos.pelines = infoInit.getPeLines()
    sequence_data.infos.seqstring = infoInit.getSeqString()
    sequence_data.infos.reconstruction = infoInit.getReconstruction()

    sequence_data.settings.readout_os = settingsInit.getReadoutOs()

    selectedGradient = Gradient()
    for instruction in list(sequence_data.instructions):
        for data in sequence_data.instructions[instruction]:
            if data[0] == "steps":
                for elem in data[1]:
                    if type(elem) == Init:
                        elem.gradients = initialization.getGradients()
                    if type(elem) == Sync:
                        elem.object = synchronization.getObject()
                        elem.time = synchronization.getStartTimeUsec()
                    if type(elem) == Rf:
                        elem.object = rfPulse.getObject()
                        elem.time = rfPulse.getStartTimeUsec()
                        if rfPulse.getAddedPhase == True :
                            elem.added_phase.type = rfPulse.getAddedPhaseType()
                            elem.added_phase.float = rfPulse.getAddedPhaseFloat()
                    if type(elem) == Grad:
                        if elem.object == "grad_slice_select":
                            selectedGradient = sliceSelectionGradient
                        if elem.object == "grad_slice_refocus":
                            selectedGradient = sliceRefocusingGradient
                        if elem.object == "grad_read_dephase":
                            selectedGradient = readoutDephasingGradient
                        if elem.object == "grad_phase_encode":
                            selectedGradient = phaseEncodingGradient
                        if elem.object == "grad_read_readout":
                            selectedGradient = readoutGradient
                        elem.action = selectedGradient.getAction()
                        elem.axis = selectedGradient.getAxis()
                        elem.time = selectedGradient.getStartTimeUsec()
                    if type(elem) == GradWithAmplitude:
                        if elem.object == "grad_slice_refocus":
                            selectedGradient = sliceSpoilingGradient
                        if elem.object == "grad_phase_encode":
                            selectedGradient = phaseSpoilingGradient
                        elem.action = selectedGradient.getAction()
                        elem.axis = selectedGradient.getAxis()
                        elem.time = selectedGradient.getStartTimeUsec()
                        elem.amplitude = selectedGradient.getAmplitudeType()
                    if type(elem) == GradWithEquation:
                        elem.amplitude.type = selectedGradient.getAmplitudeType()
                        elem.amplitude.equation = selectedGradient.getAmplitudeEquation()
                    if type(elem) == Adc:
                        elem.object = analogToDigitalConverter.getObject()
                        elem.time = analogToDigitalConverter.getStartTimeUsec()
                        elem.frequency = analogToDigitalConverter.getFrequency()
                        elem.phase = analogToDigitalConverter.getPhase()
                        elem.added_phase.type = analogToDigitalConverter.getAddedPhaseType()
                        elem.added_phase.float = analogToDigitalConverter.getAddedPhaseFloat()
                        # elem.mdh = {}
                        loop_counter = 0
                        for eventName in analogToDigitalConverter.getMdhEvents():
                            elem.mdh[eventName].type = analogToDigitalConverter.getMdhDetails()[loop_counter][0]
                            elem.mdh[eventName].counter = analogToDigitalConverter.getMdhDetails()[loop_counter][1]
                            elem.mdh[eventName].target = analogToDigitalConverter.getMdhDetails()[loop_counter][2]
                            loop_counter += 1
                    if type(elem) == Mark:
                        elem.time = marking.getStartTimeUsec()
                    if type(elem) == Submit:
                        elem.action = submit.getAction()

    gradient_counter = 0
    for object in list(sequence_data.objects):
        if list(sequence_data.objects[object])[0][1] == "rf":
            sequence_data.objects[object].duration = rfExcitation.getDuration()
            sequence_data.objects[object].array = rfExcitation.getArray()
            sequence_data.objects[object].initial_phase = rfExcitation.getInitialPhase()
            sequence_data.objects[object].thickness = rfExcitation.getThickness()
            sequence_data.objects[object].flipangle = rfExcitation.getFlipAngle()
            sequence_data.objects[object].purpose = rfExcitation.getPurpose()
        if list(sequence_data.objects[object])[0][1] == "grad":
            sequence_data.objects[object].duration = gradientList[gradient_counter].getDuration()
            sequence_data.objects[object].array = gradientList[gradient_counter].getArray()
            sequence_data.objects[object].tail = gradientList[gradient_counter].getTail()
            sequence_data.objects[object].amplitude = gradientList[gradient_counter].getAmplitude()
            gradient_counter += 1
        if list(sequence_data.objects[object])[0][1] == "adc":
            sequence_data.objects[object].duration = adcReadout.getDuration()
            sequence_data.objects[object].samples = adcReadout.getSamples()
            sequence_data.objects[object].dwelltime = adcReadout.getDwellTime()
        if list(sequence_data.objects[object])[0][1] == "sync":
            sequence_data.objects[object].duration = ttl.getDuration()
            sequence_data.objects[object].event = ttl.getEvent()
    
    return sequence_data