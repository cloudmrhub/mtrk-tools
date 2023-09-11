################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

from objects.Object import Object

class AdcObject(Object):
    # constructor
    def __init__(self, *args):
        Object.__init__(self)
        self._type = "adc"
        if len(args) == 3:
            self._duration = args[0]
            self._samples = args[1]
            self._dwell_time = args[2]
        else: 
            self._samples = 9999
            self._dwell_time = 9999
    
    # getters
    def getSamples(self):
        return self._samples

    def getDwellTime(self):
        return self._dwell_time
        

    # setters
    def setSamples(self, samples):
        self._samples = samples

    def setDwellTime(self, dwell_time):
        self._dwell_time = dwell_time
