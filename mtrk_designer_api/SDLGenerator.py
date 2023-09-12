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
from initialization.ArrayInit import ArrayInit
from initialization.EquationInit import EquationInit

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

### Defining gradient waveforms using arrays and equations
rfPulseArray = ArrayInit("text", "complex_float", 128, [3.13304e-05, 3.14159, 0.000275274, 3.14159, 0.000741752, 3.14159, 0.00140054, 3.14159, 0.00221321, 3.14159, 0.0031333, 3.14159, 0.00410657, 3.14159, 0.00507138, 3.14159, 0.00595912, 3.14159, 0.00669486, 3.14159, 0.00719792, 3.14159, 0.00738272, 3.14159, 0.00715954, 3.14159, 0.0064355, 3.14159, 0.00511552, 3.14159, 0.00310332, 3.14159, 0.00030259, 3.14159, 0.00338198, 0.0, 0.00804349, 0.0, 0.0137717, 0.0, 0.0206519, 0.0, 0.0287638, 0.0, 0.0381802, 0.0, 0.0489663, 0.0, 0.0611784, 0.0, 0.0748629, 0.0, 0.0900558, 0.0, 0.106781, 0.0, 0.125052, 0.0, 0.144867, 0.0, 0.166213, 0.0, 0.189063, 0.0, 0.213376, 0.0, 0.239097, 0.0, 0.266157, 0.0, 0.294475, 0.0, 0.323954, 0.0, 0.354486, 0.0, 0.385951, 0.0, 0.418216, 0.0, 0.451138, 0.0, 0.484565, 0.0, 0.518335, 0.0, 0.552279, 0.0, 0.586221, 0.0, 0.619982, 0.0, 0.653377, 0.0, 0.686221, 0.0, 0.718326, 0.0, 0.749508, 0.0, 0.779582, 0.0, 0.80837, 0.0, 0.835698, 0.0, 0.861398, 0.0, 0.885311, 0.0, 0.90729, 0.0, 0.927195, 0.0, 0.9449, 0.0, 0.960293, 0.0, 0.973275, 0.0, 0.983763, 0.0, 0.991689, 0.0, 0.997001, 0.0, 0.999666, 0.0, 0.999666, 0.0, 0.997001, 0.0, 0.991689, 0.0, 0.983763, 0.0, 0.973275, 0.0, 0.960293, 0.0, 0.9449, 0.0, 0.927195, 0.0, 0.90729, 0.0, 0.885311, 0.0, 0.861398, 0.0, 0.835698, 0.0, 0.80837, 0.0, 0.779582, 0.0, 0.749508, 0.0, 0.718326, 0.0, 0.686221, 0.0, 0.653377, 0.0, 0.619982, 0.0, 0.586221, 0.0, 0.552279, 0.0, 0.518335, 0.0, 0.484565, 0.0, 0.451138, 0.0, 0.418216, 0.0, 0.385951, 0.0, 0.354486, 0.0, 0.323954, 0.0, 0.294475, 0.0, 0.266157, 0.0, 0.239097, 0.0, 0.213376, 0.0, 0.189063, 0.0, 0.166213, 0.0, 0.144867, 0.0, 0.125052, 0.0, 0.106781, 0.0, 0.0900558, 0.0, 0.0748629, 0.0, 0.0611784, 0.0, 0.0489663, 0.0, 0.0381802, 0.0, 0.0287638, 0.0, 0.0206519, 0.0, 0.0137717, 0.0, 0.00804349, 0.0, 0.00338198, 0.0, 0.00030259, 3.14159, 0.00310332, 3.14159, 0.00511552, 3.14159, 0.0064355, 3.14159, 0.00715954, 3.14159, 0.00738272, 3.14159, 0.00719792, 3.14159, 0.00669486, 3.14159, 0.00595912, 3.14159, 0.00507138, 3.14159, 0.00410657, 3.14159, 0.0031333, 3.14159, 0.00221321, 3.14159, 0.00140054, 3.14159, 0.000741752, 3.14159, 0.000275274, 3.14159, 3.13304e-05, 3.14159])
grad100_2560_100 = ArrayInit("text", "float", 276, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0])
grad220_10_220 = ArrayInit("text", "float", 45, [0.0, 0.0455, 0.0909, 0.1364, 0.1818, 0.2273, 0.2727, 0.3182, 0.3636, 0.4091, 0.4545, 0.5, 0.5455, 0.5909, 0.6364, 0.6818, 0.7273, 0.7727, 0.8182, 0.8636, 0.9091, 0.9545, 1.0, 0.9545, 0.9091, 0.8636, 0.8182, 0.7727, 0.7273, 0.6818, 0.6364, 0.5909, 0.5455, 0.5, 0.4545, 0.4091, 0.3636, 0.3182, 0.2727, 0.2273, 0.1818, 0.1364, 0.0909, 0.0455, 0.0])
grad220_80_220 = ArrayInit("text", "float", 52, [0.0, 0.0455, 0.0909, 0.1364, 0.1818, 0.2273, 0.2727, 0.3182, 0.3636, 0.4091, 0.4545, 0.5, 0.5455, 0.5909, 0.6364, 0.6818, 0.7273, 0.7727, 0.8182, 0.8636, 0.9091, 0.9545, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9545, 0.9091, 0.8636, 0.8182, 0.7727, 0.7273, 0.6818, 0.6364, 0.5909, 0.5455, 0.5, 0.4545, 0.4091, 0.3636, 0.3182, 0.2727, 0.2273, 0.1818, 0.1364, 0.0909, 0.0455, 0.0])
grad30_3840_30 = ArrayInit("text", "float", 390, [0.0, 0.3333, 0.6667, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.6667, 0.3333, 0.0])
arrayList = [rfPulseArray, grad100_2560_100, grad220_10_220, grad220_80_220, grad30_3840_30]
phaseEncodingEquation = EquationInit("0.3378125*(ctr(1)-64.5)")
equationList = [phaseEncodingEquation]

### filling instructions in an already created SDL file
sequence_data = miniFlashModifier(sequence_data, fileInit, infoInit, settingsInit, \
                                initialization, synchronization, rfPulse, \
                                sliceSelectionGradient, sliceRefocusingGradient, \
                                readoutDephasingGradient, phaseEncodingGradient, \
                                readoutGradient, sliceSpoilingGradient, \
                                phaseSpoilingGradient, analogToDigitalConverter, \
                                marking, submit, rfExcitation, gradientList, adcReadout, \
                                ttl, arrayList, equationList)

### creating SDL file correcponding to instructions


### writing of json schema to SDL file with formatting options
with open('C:\\Users\\artiga02\\mtrk_seq\\examples\\test.mtrk', 'w') as sdlFileOut:
    options = jsbeautifier.default_options()
    options.indent_size = 4
    data_to_print = jsbeautifier.beautify(json.dumps(sequence_data.model_dump(mode="json")), options)
    sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic 
  
  