################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################  

import json
import jsbeautifier
import re
from pprint import pprint
from devtools import debug

from initialization.FileInit import FileInit
from initialization.InfoInit import InfoInit
from initialization.SettingsInit import SettingsInit

from steps.Initialization import Initialization
from steps.Synchronization import Synchronization
from steps.RfPulse import RfPulse 
from steps.Gradient import Gradient
from steps.AnalogToDigitalConverter import AnalogToDigitalConverter
from steps.Marking import Marking

from SDL_read_write.pydanticSDLHandler import *


### loading of sequence data
with open('C:\\Users\\artiga02\\mtrk_seq\\examples\\miniflash.mtrk') as sdlFile:
    sdlData = json.load(sdlFile)
    sequence_data = PulseSequence(**sdlData)

    # printing debug info
    # debug(sequence_data.instructions)

    # modifying of a value
    # sequence_data.file.format = "Custom!"
    # print(sequence_data.file.format)


### Defining SDL file initialization
fileInit = FileInit(1, "abc", "Skyra-XQ")
settingsInit = SettingsInit(2)
infoInit = InfoInit("MiniFlash equivalent", 2, 300, 128, "YARRA", "%SiemensIceProgs%\\IceProgram2D")


### Defining sequence
# initialization
initialization = Initialization("logical")

# synchronization
synchronization = Synchronization("ttl", 0)

# RF axis
rfPulse = RfPulse("rf_excitation", 100,True,["float", 0.0])

# slice axis
sliceSelectionGradient = Gradient("slice","grad_slice_select", 0)
sliceRefocusingGradient = Gradient("slice","grad_slice_refocus", 2760)
sliceSpoilingGradient = Gradient("slice","grad_slice_refocus", 13300, "flip")

# readout axis
readoutDephasingGradient = Gradient("read","grad_read_dephase", 2660)
readoutGradient = Gradient("read","grad_read_readout", 9430)

# phase axis
phaseEncodingGradient = Gradient("phase","grad_phase_encode", 2660, "equation", "phaseencoding")
phaseSpoilingGradient = Gradient("phase","grad_phase_encode", 13300, "flip")

# analog to digital converter
analogToDigitalConverter = AnalogToDigitalConverter("adc_readouts", 9460, 0, 0, "float", 0)

# marking
marking = Marking(20000)


### filling instructions in an already created SDL file
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

### creating SDL file correcponding to instructions


### writing of json schema to SDL file with formatting options
with open('C:\\Users\\artiga02\\mtrk_seq\\examples\\test.mtrk', 'w') as sdlFileOut:
    options = jsbeautifier.default_options()
    options.indent_size = 4
    data_to_print = jsbeautifier.beautify(json.dumps(sequence_data.model_dump(mode="json")), options)
    sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic 
  
  