################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

from objects.Object import Object

class GradientObject(Object):
    # constructor
    def __init__(self, *args):
        Object.__init__(self)
        self._type = "grad"
        if len(args) == 4:
            self._duration = args[0]
            self._array = args[1]
            self._tail = args[2]
            self._amplitude = args[3]
        else: 
            self._array = "default_array"
            self._tail = 9999
            self._amplitude = -9999.99
    
    # getters
    def getArray(self):
        return self._array
    
    def getTail(self):
        return self._tail

    def getAmplitude(self):
        return self._amplitude
    
    # setters
    def setArray(self, array):
        self._array = array
    
    def setTail(self, tail):
        self._tail = tail

    def setAmplitude(self, amplitude):
        self._amplitude = amplitude