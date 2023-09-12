################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

class EquationInit:
    # constructor
    def __init__(self, *args):
        if len(args) == 1:
            self._equation = args[0]
        else:    
            self._equation = "default_equation"


    # getters
    def getEquation(self):
        return self._equation
    

    # setters
    def setEquation(self, equation):
        self._equation = equation