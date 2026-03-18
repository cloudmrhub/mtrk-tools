################################################################################
### mtrk project                                                             ###
### Version 0.2.0                                                            ###
### Anais Artiges and the mtrk project team at NYU - 07/22/2025              ###
################################################################################   

import json
import jsbeautifier
import re

from SDL_read_write.pydanticSDLHandler import *

def modifySetting(inputFileName = 'se2d.mtrk', key = "TE", value = 20):
    """
    Modify a chosen setting in the input file.
    
    Args:
        inputFileName (str): Path to the input settings file.
        key (str): The key in the settings to modify.
        value (int): The new value to set for the key.
    """
    with open(inputFileName, 'r') as sdlFile:
        sdlData = json.load(sdlFile)
        sequence_data = PulseSequence(**sdlData)
    
    # Example modification: increment readout_os by 1
    if key in str(sequence_data.settings):
        sequence_data.settings.set(key, value)

    with open(inputFileName, 'w') as sdlFileOut:
        options = jsbeautifier.default_options()
        options.indent_size = 4
        data_to_print = jsbeautifier.beautify(json.dumps(sequence_data.model_dump(mode="json")), options)
        sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) #purely aesthetic 

## Test
#modifySetting(inputFileName='se2d.mtrk', key='TE', value=20000)


