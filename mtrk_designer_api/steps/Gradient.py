################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

from steps.Step import Step

class Gradient(Step):
    # constructor
    def __init__(self, *args):
        Step.__init__(self)
        self._action = "grad"
        if len(args) == 3:
            self._axis = args[0]
            self._object = args[1]
            self._start_time_usec = args[2]
        elif len(args) == 4:
            self._axis = args[0]
            self._object = args[1]
            self._start_time_usec = args[2]
            self._amplitude_type = args[3]
        elif len(args) == 5:
            self._axis = args[0]
            self._object = args[1]
            self._start_time_usec = args[2]
            self._amplitude_type = args[3]
            self._amplitude_equation = args[4]
        else:
            self._axis = "default_axis"
            self._amplitude_type = ""
            self._amplitude_equation = ""
    
    # getters
    def getAxis(self):
        return self._axis
    
    def getAmplitudeType(self):
        return self._amplitude_type
    
    def getAmplitudeEquation(self):
        return self._amplitude_equation

    # setters
    def setAxis(self, axis):
        self._axis = axis

    def setAmplitudeType(self, amplitude_type):
        self._amplitude_type = amplitude_type
    
    def setAmplitudeEquation(self, amplitude_equation):
        self._amplitude_equation = amplitude_equation
  