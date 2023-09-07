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

from steps.RfPulse import RfPulse 
from steps.Gradient import Gradient
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

# Defining sequence

# RF axis
rfPulse = RfPulse()
rfPulse.generateExcitationPulse(100,True,["float", 0.0])

# slice axis
sliceSelectionGradient = Gradient()
sliceSelectionGradient.generateGradient("slice","grad_slice_select", 0)
sliceRefocusingGradient = Gradient()
sliceRefocusingGradient.generateGradient("slice","grad_slice_refocus", 2760)
sliceSpoilingGradient = Gradient()
sliceSpoilingGradient.generateGradientAmplitude("slice","grad_slice_refocus", 13300, "flip")

# readout axis
readoutDephasingGradient = Gradient()
readoutDephasingGradient.generateGradient("read","grad_read_dephase", 2660)
readoutGradient = Gradient()
readoutGradient.generateGradient("read","grad_read_readout", 9430)

# phase axis
phaseEncodingGradient = Gradient()
phaseEncodingGradient.generateGradientEquation("phase","grad_phase_encode", 2660, "phaseencoding")
phaseSpoilingGradient = Gradient()
phaseSpoilingGradient.generateGradientAmplitude("phase","grad_phase_encode", 13300, "flip")


# filling instructions on  an already created SDL file
# temporarily relying on classes to discriminate between spoiling and other gradients
selectedGradient = Gradient()
for instruction in list(sequence_data.instructions):
    for data in sequence_data.instructions[instruction]:
        if data[0] == "steps":
            for elem in data[1]:
                if type(elem) == Rf:
                    elem.action = rfPulse.getAction()
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
                    elem.action = selectedGradient.getAction()
                    elem.axis = selectedGradient.getAxis()
                    elem.time = selectedGradient.getStartTimeUsec()
                if type(elem) == GradWithAmplitude:
                    if elem.object == "grad_slice_refocus":
                        selectedGradient = sliceSpoilingGradient
                    elem.action = selectedGradient.getAction()
                    elem.axis = selectedGradient.getAxis()
                    elem.time = selectedGradient.getStartTimeUsec()
                    elem.amplitude = selectedGradient.getAmplitudeType()


### writing of json schema to SDL file with formatting options
with open('C:\\Users\\artiga02\\mtrk_seq\\examples\\test.mtrk', 'w') as sdlFileOut:
    options = jsbeautifier.default_options()
    options.indent_size = 4
    data_to_print = jsbeautifier.beautify(json.dumps(sequence_data.model_dump(mode="json")), options)
    sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic 
  