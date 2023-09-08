################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

from steps.Step import Step

class AnalogToDigitalConverter(Step):
    # constructor
    def __init__(self, *args):
        Step.__init__(self)
        self._action = "adc"
        if len(args) == 6:
            self._object = args[0]
            self._start_time_usec = args[1]
            self._frequency = args[2]
            self._phase = args[3]
            self._added_phase_type = args[4]
            self._added_phase_float = args[5]
            self._mdh_events = ["line", "first_scan_slice", "last_scan_slice"]
            self._mdh_details = [["counter", 1, None], ["counter", 1, 0], ["counter", 1, 127]]
        else:
            self._object = "default"
            self._start_time_usec = 0
            self._frequency = 0
            self._phase = 0
            self._added_phase_type = "default"
            self._added_phase_float = 0
            self._mdh_events = {}
            self._mdh_details = {}
    
    # getters
    def getObject(self):
        return self._object
    
    def getStartTimeUsec(self):
        return self._start_time_usec
    
    def getFrequency(self):
        return self._frequency
    
    def getPhase(self):
        return self._phase
    
    def getAddedPhaseType(self):
        return self._added_phase_type
    
    def getAddedPhaseFloat(self):
        return self._added_phase_float
    
    def getMdhEvents(self):
        return self._mdh_events
    
    def getMdhDetails(self):
        return self._mdh_details

    # setters
    def setObject(self, object):
        self._object = object

    def setStartTimeUsec(self, start_time_usec):
        self._start_time_usec = start_time_usec

    def setFrequency(self, frequency):
        self._frequency = frequency

    def setPhase(self, phase):
        self._phase = phase

    def setAddedPhaseType(self, added_phase_type):
        self._added_phase_type = added_phase_type

    def setAddedPhaseFloat(self, added_phase_float):
        self._added_phase_float = added_phase_float

    def setMdhEvents(self, mdh_events):
        self._mdh_events = mdh_events

    def setMdhDetails(self, mdh_details):
        self._mdh_details = mdh_details