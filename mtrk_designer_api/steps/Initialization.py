################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

from steps.Step import Step

class Initialization(Step):
    # constructor
    def __init__(self, *args):
        Step.__init__(self)
        self._action = "init"
        if len(args) == 1:
           self._gradients = args[0]
        else: 
            self._gradients = "default"
    
    # getters
    def getGradients(self):
        return self._gradients
    
    # setters
    def setGradients(self, gradients):
        self._gradients = gradients