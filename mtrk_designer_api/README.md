# Description
mtrk_designer_api contains the tools to design an MRI pulse sequence, to write it as an SDL file (Json-based, .mtrk file), to convert this file to Pulseq format, and to connect to mtrk_designer_gui which is a graphical user interface (GUI) for MRI pulse sequence development. 

# Contents
This repository contains:
- SDL_read_write/pydanticSDLHandler: a set of tools to read and write SDL files using Pydantic,
- miniFlashModifier: a prototype file that reads the existing miniflash.mtrk file (available in init_data) and modifies it,
- mtrkConsoleUI: a console interface to create an SDL file,
- backendToUI: tools to connect with the GUI,
- camrieConverter (WIP): a prototype tool to convert SDL files to PSUdoMRI format used in Camrie,
- pulseqConverter: a tool to convert SDL files to Pulseq files using PyPulseq,
- RfPulseGenerator (WIP): a prototype to generate RF pulses,
- SDLGenerator: a file to test and call all the tools described before (main).

Additionnaly, requirements.txt helps setting the local environment by intalling the right dependencies, and Doxyfile allows to generate the doxygen documentation. 

# How to run it
For this first prototype, it is necessary to open SDLGenerator.py and uncomment the selected action (miniFlashModifier, mtrkConsoleUI, camrieConverter, or pulseqConverter, lines 165-483) to run it. Only one action can be uncommented at a time (by default, pulseqConverter is enabled). The local paths need to be adapted for input (line 53), and output (line 187). If no input is needed (creation of a new file), the miniflash.mtrk file should be used as an input for initialization. 

# Questions?
You can contact me at anais.artiges@nyulangone.org
