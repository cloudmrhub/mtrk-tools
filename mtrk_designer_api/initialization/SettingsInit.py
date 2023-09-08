################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

class SettingsInit:
    # constructor
    def __init__(self, *args):
        if len(args) == 1:
            self._readout_os = args[0]
        else:
            self._readout_os = 99999
    
    # getters
    def getReadoutOs(self):
        return self._readout_os
    
    # setters
    def setReadoutOs(self, readout_os):
        self._readout_os = readout_os