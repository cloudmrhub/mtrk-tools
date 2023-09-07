################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

from steps.Step import Step

class Gradient(Step):
    # default constructor
    def __init__(self):
        Step.__init__(self)
        self._action = "grad"
        self._axis = "default_axis"
        self._amplitude_type = ""
        self._amplitude_equation = ""
    
    # Generation of generic gradient parameters
    def generateGradient(self, axis, object, start_time_usec):
        self._axis = axis
        self._object = object
        self._start_time_usec = start_time_usec

    def generateGradientAmplitude(self, axis, object, start_time_usec, amplitude_type):
        self._axis = axis
        self._object = object
        self._start_time_usec = start_time_usec
        self._amplitude_type = amplitude_type

    def generateGradientEquation(self, axis, object, start_time_usec, amplitude_equation):
        self._axis = axis
        self._object = object
        self._start_time_usec = start_time_usec
        self._amplitude_type = "equation"
        self._amplitude_equation = amplitude_equation

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
  