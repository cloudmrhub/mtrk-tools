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
from mtrkConsoleUI import mtrkConsoleUI
from camrieConverter import camrieConverter
from pulseqConverter import pulseqConverter

from SDL_read_write.pydanticSDLHandler import *


### loading of sequence data
with open('C:\\Users\\artiga02\\mtrk_seq\\examples\\se2d.mtrk') as sdlFile:
    sdlData = json.load(sdlFile)
    sequence_data = PulseSequence(**sdlData)


### Defining SDL file initialization
fileInit = File(version = 1, measurement = "abc", system = "Skyra-XQ")
settingsInit = Settings(readout_os = 2)
infoInit = Info(description = "MiniFlash equivalent", slices = 2, fov = 300, \
                pelines = 128, seqstring = "YARRA", reconstruction = \
                "%SiemensIceProgs%\\IceProgram2D")


### Defining sequence (instructions field)
# loops
mainLoop = Loop(counter = 2, range = 1, \
                steps = [Step(action = "run_block", \
                             block = "block_phaseEncoding")])
PELoop = Loop(counter = 2, range = 128, \
              steps = [Step(action = "run_block", block = "block_TR")])

# rf spoiling
rfSpoiling = Calc(type = "float_rfspoil", float = 0, increment = 50)

# initialization
initialization = Init(gradients = "logical")

# synchronization
synchronization = Sync(object = "ttl", time = 0)

# RF axis
rfPulse = Rf(object = "rf_excitation", time = 100, \
             added_phase = AddedPhase(type = "float", float = 0))

# slice axis
sliceSelectionGradient = Grad(axis = "slice", object = "grad_slice_select", \
                              time = 0)
sliceRefocusingGradient = Grad(axis = "slice", object = "grad_slice_refocus", \
                               time = 2760)
sliceSpoilingGradient = GradWithAmplitude(axis = "slice", \
                                          object = "grad_slice_refocus", \
                                          time = 13300, amplitude = "flip")

# readout axis
readoutDephasingGradient = Grad(axis = "read", object = "grad_read_dephase", \
                                time = 2660)
readoutGradient = Grad(axis = "read", object = "grad_read_readout", \
                       time = 9430)

# phase axis
phaseEncodingGradient = GradWithAmplitude(axis = "phase", \
                                          object = "grad_phase_encode", \
                                          time = 2660, \
                                          amplitude = Amplitude( \
                                                   type = "equation", \
                                                   equation = "phaseencoding") )
phaseSpoilingGradient = GradWithAmplitude(axis = "phase", \
                                          object = "grad_phase_encode", \
                                          time = 13300, amplitude = "flip")

# analog to digital converter
mdhOptionsDict = \
    { "line": MdhOption(type = "counter", counter = 1), \
      "first_scan_slice": MdhOption(type = "counter", counter = 1, target = 0),\
      "last_scan_slice": MdhOption(type = "counter", counter = 1, target = 127)}
analogToDigitalConverter = Adc(object = "adc_readouts", time = 9460, \
                               frequency = 0, phase = 0, \
                               added_phase = AddedPhase(type = "float", \
                                                        float = 0.0), \
                               mdh = mdhOptionsDict)

# marking
marking = Mark(time = 20000)

# submitting
submit = Submit()

### Defining objects to be used in the creation of real time events
rfExcitation = RfExcitation(duration = 2560, array = "rfpulse", \
                            initial_phase = 0, thickness = 5, flipangle = 15, \
                            purpose = "excitation")
gradSliceSelect = GradientObject(duration = 2660, array = "grad_100_2560_100", \
                                 tail = 0, amplitude = 4.95)
gradSliceRefocus = GradientObject(duration = 300, array = "grad_220_80_220", \
                                  tail = 0, amplitude = -21.96)
gradReadDephase = GradientObject(duration = 230, array = "grad_220_10_220", \
                                 tail = 0, amplitude = -21.96)
gradReadReadout = GradientObject(duration = 3870, array = "grad_30_3840_30", \
                                 tail = 0, amplitude = 2.61)
gradPhaseEncode = GradientObject(duration = 230, array = "grad_220_10_220", \
                                 tail = 0, amplitude = 10.00)
gradientList = [gradSliceSelect, gradSliceRefocus, gradReadDephase, gradReadReadout, gradPhaseEncode]
adcReadout = AdcReadout(duration = 3840, samples = 128, dwelltime = 30000)
ttl = Ttl(duration = 10, event = "osc0")

### Defining gradient waveforms using arrays and equations
rfPulseArray = GradientTemplate(encoding = "text", type = "complex_float", \
                                size = 128, data = [3.13304e-05, 3.14159, 0.000275274, 3.14159, 0.000741752, 3.14159, 0.00140054, 3.14159, 0.00221321, 3.14159, 0.0031333, 3.14159, 0.00410657, 3.14159, 0.00507138, 3.14159, 0.00595912, 3.14159, 0.00669486, 3.14159, 0.00719792, 3.14159, 0.00738272, 3.14159, 0.00715954, 3.14159, 0.0064355, 3.14159, 0.00511552, 3.14159, 0.00310332, 3.14159, 0.00030259, 3.14159, 0.00338198, 0.0, 0.00804349, 0.0, 0.0137717, 0.0, 0.0206519, 0.0, 0.0287638, 0.0, 0.0381802, 0.0, 0.0489663, 0.0, 0.0611784, 0.0, 0.0748629, 0.0, 0.0900558, 0.0, 0.106781, 0.0, 0.125052, 0.0, 0.144867, 0.0, 0.166213, 0.0, 0.189063, 0.0, 0.213376, 0.0, 0.239097, 0.0, 0.266157, 0.0, 0.294475, 0.0, 0.323954, 0.0, 0.354486, 0.0, 0.385951, 0.0, 0.418216, 0.0, 0.451138, 0.0, 0.484565, 0.0, 0.518335, 0.0, 0.552279, 0.0, 0.586221, 0.0, 0.619982, 0.0, 0.653377, 0.0, 0.686221, 0.0, 0.718326, 0.0, 0.749508, 0.0, 0.779582, 0.0, 0.80837, 0.0, 0.835698, 0.0, 0.861398, 0.0, 0.885311, 0.0, 0.90729, 0.0, 0.927195, 0.0, 0.9449, 0.0, 0.960293, 0.0, 0.973275, 0.0, 0.983763, 0.0, 0.991689, 0.0, 0.997001, 0.0, 0.999666, 0.0, 0.999666, 0.0, 0.997001, 0.0, 0.991689, 0.0, 0.983763, 0.0, 0.973275, 0.0, 0.960293, 0.0, 0.9449, 0.0, 0.927195, 0.0, 0.90729, 0.0, 0.885311, 0.0, 0.861398, 0.0, 0.835698, 0.0, 0.80837, 0.0, 0.779582, 0.0, 0.749508, 0.0, 0.718326, 0.0, 0.686221, 0.0, 0.653377, 0.0, 0.619982, 0.0, 0.586221, 0.0, 0.552279, 0.0, 0.518335, 0.0, 0.484565, 0.0, 0.451138, 0.0, 0.418216, 0.0, 0.385951, 0.0, 0.354486, 0.0, 0.323954, 0.0, 0.294475, 0.0, 0.266157, 0.0, 0.239097, 0.0, 0.213376, 0.0, 0.189063, 0.0, 0.166213, 0.0, 0.144867, 0.0, 0.125052, 0.0, 0.106781, 0.0, 0.0900558, 0.0, 0.0748629, 0.0, 0.0611784, 0.0, 0.0489663, 0.0, 0.0381802, 0.0, 0.0287638, 0.0, 0.0206519, 0.0, 0.0137717, 0.0, 0.00804349, 0.0, 0.00338198, 0.0, 0.00030259, 3.14159, 0.00310332, 3.14159, 0.00511552, 3.14159, 0.0064355, 3.14159, 0.00715954, 3.14159, 0.00738272, 3.14159, 0.00719792, 3.14159, 0.00669486, 3.14159, 0.00595912, 3.14159, 0.00507138, 3.14159, 0.00410657, 3.14159, 0.0031333, 3.14159, 0.00221321, 3.14159, 0.00140054, 3.14159, 0.000741752, 3.14159, 0.000275274, 3.14159, 3.13304e-05, 3.14159])
grad100_2560_100 = GradientTemplate(encoding = "text", type = "float", \
                                    size = 276, data = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0])
grad220_10_220 = GradientTemplate(encoding = "text", type = "float", size = 45,\
                                  data = [0.0, 0.0455, 0.0909, 0.1364, 0.1818, 0.2273, 0.2727, 0.3182, 0.3636, 0.4091, 0.4545, 0.5, 0.5455, 0.5909, 0.6364, 0.6818, 0.7273, 0.7727, 0.8182, 0.8636, 0.9091, 0.9545, 1.0, 0.9545, 0.9091, 0.8636, 0.8182, 0.7727, 0.7273, 0.6818, 0.6364, 0.5909, 0.5455, 0.5, 0.4545, 0.4091, 0.3636, 0.3182, 0.2727, 0.2273, 0.1818, 0.1364, 0.0909, 0.0455, 0.0])
grad220_80_220 = GradientTemplate(encoding = "text", type = "float", size = 52,\
                                  data = [0.0, 0.0455, 0.0909, 0.1364, 0.1818, 0.2273, 0.2727, 0.3182, 0.3636, 0.4091, 0.4545, 0.5, 0.5455, 0.5909, 0.6364, 0.6818, 0.7273, 0.7727, 0.8182, 0.8636, 0.9091, 0.9545, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9545, 0.9091, 0.8636, 0.8182, 0.7727, 0.7273, 0.6818, 0.6364, 0.5909, 0.5455, 0.5, 0.4545, 0.4091, 0.3636, 0.3182, 0.2727, 0.2273, 0.1818, 0.1364, 0.0909, 0.0455, 0.0])
grad30_3840_30 = GradientTemplate(encoding = "text", type = "float", \
                                  size = 390, data = [0.0, 0.3333, 0.6667, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.6667, 0.3333, 0.0])
arrayList = [rfPulseArray, grad100_2560_100, grad220_10_220, grad220_80_220, \
             grad30_3840_30]
phaseEncodingEquation = Equation(equation = "0.3378125*(ctr(1)-64.5)")
equationList = [phaseEncodingEquation]

### filling instructions in an already created SDL file
# sequence_data = miniFlashModifier(mainLoop, PELoop, \
#                                   sequence_data, fileInit, infoInit, settingsInit, \
#                                   rfSpoiling, initialization, synchronization, rfPulse, \
#                                   sliceSelectionGradient, sliceRefocusingGradient, \
#                                   readoutDephasingGradient, phaseEncodingGradient, \
#                                   readoutGradient, sliceSpoilingGradient, \
#                                   phaseSpoilingGradient, analogToDigitalConverter, \
#                                   marking, submit, rfExcitation, gradientList, adcReadout, \
#                                   ttl, arrayList, equationList)

### creating SDL file correcponding to instructions
# sequence_data = mtrkConsoleUI(sequence_data)

### converting SDL format to PSUdoMRI format
# camrieConverter(sequence_data)

### converting SDL format to Pulseq format
pulseqConverter(sequence_data)

### writing of json schema to SDL file with formatting options
with open('C:\\Users\\artiga02\\mtrk_seq\\examples\\test.mtrk', 'w') as sdlFileOut:
    options = jsbeautifier.default_options()
    options.indent_size = 4
    data_to_print = jsbeautifier.beautify(json.dumps(sequence_data.model_dump(mode="json")), options)
    sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic 
  
  