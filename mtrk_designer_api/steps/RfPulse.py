################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

from steps.Step import Step

class RfPulse(Step):
    # constructor
    def __init__(self, *args):
        Step.__init__(self)
        self._action = "rf"
        if len(args) == 3:
            self._object = args[0]
            self._start_time_usec = args[1]
            self._added_phase = args[2]
        if len(args) == 4:
            self._object = args[0]
            self._start_time_usec = args[1]
            self._added_phase = args[2]
            self._added_phase_type = args[3][0]
            self._added_phase_float = args[4][1]
        else:
            self._added_phase = True
            self._added_phase_type = "undefined"
            self._added_phase_float = 0.0 ### unclear!
    
    # Generation of RF pulse parameters
    def __init__(self, object, start_time_usec, added_phase, added_phase_parameters):
        self._object = object
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