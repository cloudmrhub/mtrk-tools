################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

from steps.Step import Step

class Synchronization(Step):
    # constructor
    def __init__(self, *args):
        Step.__init__(self)
        self._action = "sync"
        if len(args) == 2:
            self._object = args[0]
            self._start_time_usec = args[1]
        else:
            self._object = "default"
            self._start_time_usec = 0
    
    # initialization of synchronization
    def __init__(self, object, start_time_usec):
        self._object = object
        self._start_time_usec = start_time_usec
    
    # getters
    def getObject(self):
        return self._object
    
    def getStartTimeUsec(self):
        return self._start_time_usec
    
    # setters
    def setObject(self, object):
        self._object = object

    def setStartTimeUsec(self, start_time_usec):
        self._start_time_usec = start_time_usec