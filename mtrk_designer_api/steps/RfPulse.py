################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

from steps.Step import Step

class RfPulse(Step):
    # default constructor
    def __init__(self):
        Step.__init__(self)
        self._action = "rf"
        self._added_phase = True
        self._added_phase_type = "undefined"
        self._added_phase_float = 0.0 ### unclear!
    
    # Generation of excitation pulse parameters
    def generateExcitationPulse(self, start_time_usec, added_phase, added_phase_parameters):
        self._object = "rf_excitation"
        self._start_time_usec = start_time_usec
        self._added_phase = added_phase
        if added_phase == True:
            self._added_phase_type = added_phase_parameters[0]
            self._added_phase_float = added_phase_parameters[1]
        else:
            pass
    
    # Generation of refocusing pulse parameters
    def generateRefocusingPulse(self, start_time_usec, added_phase, added_phase_parameters):
        self._object = "rf_refocusing"
        self._start_time_usec = start_time_usec
        self._added_phase = added_phase
        if added_phase == True:
            self._added_phase_type = added_phase_parameters[0]
            self._added_phase_float = added_phase_parameters[1]
        else:
            pass

    # getters
    def getAddedPhase(self):
        return self._added_phase
    
    def getAddedPhaseType(self):
        return self._added_phase_type

    def getAddedPhaseFloat(self):
        return self._added_phase_float
    
    # setters
    def setAddedPhase(self, added_phase):
        self._added_phase = added_phase
    
    def setAddedPhaseType(self, added_phase_type):
        self._added_phase_type = added_phase_type

    def setAddedPhaseFloat(self, added_phase_float):
        self.added_phase_float = added_phase_float