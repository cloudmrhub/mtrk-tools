################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

class Step:
    # default constructor
    def __init__(self):
        self._action = "default_step"
        self._object = "default_step"
        self._start_time_usec = 0
    
    # getters
    def getAction(self):
        return self._action
    
    def getObject(self):
        return self._object
    
    def getStartTimeUsec(self):
        return self._start_time_usec
    
    # setters
    def setAction(self, action):
        self._action = action
    
    def setObject(self, object):
        self._object = object
    
    def setStartTimeUsec(self, start_time_usec):
        self._start_time_usec = start_time_usec
    