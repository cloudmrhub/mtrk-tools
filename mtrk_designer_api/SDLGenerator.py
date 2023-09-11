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

from miniFlashModifier import miniFlashModifier

from initialization.FileInit import FileInit
from initialization.InfoInit import InfoInit
from initialization.SettingsInit import SettingsInit

from steps.Step import Step as StepType
from steps.Initialization import Initialization
from steps.Synchronization import Synchronization
from steps.RfPulse import RfPulse 
from steps.Gradient import Gradient
from steps.AnalogToDigitalConverter import AnalogToDigitalConverter
from steps.Marking import Marking

from objects.RfObject import RfObject
from objects.GradientObject import GradientObject as GradientObjectType
from objects.AdcObject import AdcObject
from objects.SynchronizationObject import SynchronizationObject

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


### Defining sequence (instructions field)
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

# submitting
submit = StepType("submit")

### Defining objects to be used in the creation of real time events
rfExcitation = RfObject(2560, "rfpulse", 0, 5, 15, "excitation")
gradSliceSelect = GradientObjectType(2660, "grad_100_2560_100", 0, 4.95)
gradSliceRefocus = GradientObjectType(300, "grad_220_80_220", 0, -21.96)
gradReadDephase = GradientObjectType(230, "grad_220_10_220", 0, -21.96)
gradReadReadout = GradientObjectType(3870, "grad_30_3840_30", 0, 2.61)
gradPhaseEncode = GradientObjectType(230, "grad_220_10_220", 0, 10.00)
gradientList = [gradSliceSelect, gradSliceRefocus, gradReadDephase, gradReadReadout, gradPhaseEncode]
adcReadout = AdcObject(3840, 128, 30000)
ttl = SynchronizationObject(10, "osc0")

### filling instructions in an already created SDL file
sequence_data = miniFlashModifier(sequence_data, fileInit, infoInit, settingsInit, \
                                initialization, synchronization, rfPulse, \
                                sliceSelectionGradient, sliceRefocusingGradient, \
                                readoutDephasingGradient, phaseEncodingGradient, \
                                readoutGradient, sliceSpoilingGradient, \
                                phaseSpoilingGradient, analogToDigitalConverter, \
                                marking, submit, rfExcitation, gradientList, adcReadout, \
                                ttl)

### creating SDL file correcponding to instructions


### writing of json schema to SDL file with formatting options
with open('C:\\Users\\artiga02\\mtrk_seq\\examples\\test.mtrk', 'w') as sdlFileOut:
    options = jsbeautifier.default_options()
    options.indent_size = 4
    data_to_print = jsbeautifier.beautify(json.dumps(sequence_data.model_dump(mode="json")), options)
    sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic 
  
  