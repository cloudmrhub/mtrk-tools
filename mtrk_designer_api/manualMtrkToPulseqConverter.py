################################################################################
### mtrk project - Pypulseq-based conversion tool from SDL to Pulseq.        ###
### Version 0.1.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 04/29/2024              ###
################################################################################

import json
from SDL_read_write.pydanticSDLHandler import *
from mtrkToPulseqConverter import *

## Name of the file to convert from mtrk to Pulseq format
fileToConvert = 'C:/Users/artiga02/Downloads/output_sdl_file_radial.mtrk'
outputFile = 'C:/Users/artiga02/Downloads/output_sdl_file_radial.seq'

def manualMtrkToPulseqConverter(fileToConvert = "test.mtrk", outputFile = "test.seq"):
    """
    Converts the given sequence data to a Pulseq format.

    Args:
        sequence_data (dict): The sequence data to be converted.

    Returns:
        None
    """
    print("Converting mtrk to Pulseq format")
    print("mtrk file to convert: ", fileToConvert)
    print("Pulseq file to create: ", outputFile)

    with open(fileToConvert) as sdlFile:
        sdlData = json.load(sdlFile)
        sequence_data = PulseSequence(**sdlData)

    fillSequence(sequence_data, 
                 plot=True, 
                 write_seq=True,
                 seq_filename=outputFile)


################################################################################
## Converting the file from mtrk to Pulseq format using command line for input
################################################################################
print("Converting mtrk to Pulseq format")
print("mtrk file to convert: ")
fileToConvert = input()
print("Pulseq file to create: ")
outputFile = input()

manualMtrkToPulseqConverter(fileToConvert, outputFile)