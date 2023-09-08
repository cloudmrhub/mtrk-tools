################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

from steps.Step import Step

class Marking(Step):
    # constructor
    def __init__(self, *args):
        Step.__init__(self)
        self._action = "mark"
        if len(args) == 1:
            self._start_time_usec = args[0] # defining TR, unclear
        else:
            self._start_time_usec = 0
    
    # getters
    def getStartTimeUsec(self):
        return self._start_time_usec
    
    # setters
    def setStartTimeUsec(self, start_time_usec):
        self._start_time_usec = start_time_usec