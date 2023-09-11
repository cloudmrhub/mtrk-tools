################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

class Object:
    # constructor
    def __init__(self, *args):
        self._type = "default_type"
        self._duration = 9999
    
    # getters
    def getType(self):
        return self._type
    
    def getDuration(self):
        return self._duration
    
    # setters
    def setType(self, type):
        self._type = type
    
    def setDuration(self, duration):
        self._duration = duration
    