################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

from objects.Object import Object

class SynchronizationObject(Object):
    # constructor
    def __init__(self, *args):
        Object.__init__(self)
        self._type = "sync"
        if len(args) == 2:
            self._duration = args[0]
            self._event = args[1]
        else: 
            self._event = "default_event"
    
    # getters
    def getEvent(self):
        return self._event
    

    # setters
    def setEvent(self, event):
        self._event = event
    