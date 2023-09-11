################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

from objects.Object import Object

class RfObject(Object):
    # constructor
    def __init__(self, *args):
        Object.__init__(self)
        self._type = "rf"
        if len(args) == 6:
            self._duration = args[0]
            self._array = args[1]
            self._initial_phase = args[2]
            self._thickness = args[3]
            self._flip_angle = args[4]
            self._purpose = args[5]
        else: 
            self._array = "default_array"
            self._initial_phase = 9999
            self._thickness = 9999
            self._flip_angle = 9999
            self._purpose = "default_purpose"
    
    # getters
    def getArray(self):
        return self._array
    
    def getInitialPhase(self):
        return self._initial_phase

    def getThickness(self):
        return self._thickness
        
    def getFlipAngle(self):
        return self._flip_angle
    
    def getPurpose(self):
        return self._purpose
    
    # setters
    def setArray(self, array):
        self._array = array
    
    def setInitialPhase(self, initial_phase):
        self._initial_phase = initial_phase

    def setThickness(self, thickness):
        self._thickness = thickness

    def setFlipAngle(self, flip_angle):
        self._flip_angle = flip_angle

    def setPurpose(self, purpose):
        self._purpose = purpose
    