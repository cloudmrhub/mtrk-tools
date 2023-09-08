################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

class FileInit:
    # constructor
    def __init__(self, *args):
        if len(args) == 3:
            self._format = "mtrk-SDL"
            self._version = args[0]
            self._measurement = args[1]
            self._system = args[2]
        else:    
            self._format = "default"
            self._version = 9999
            self._measurement = "default"
            self._system = "default"

    # getters
    def getFormat(self):
        return self._format
    
    def getVersion(self):
        return self._version
    
    def getMeasurement(self):
        return self._measurement
    
    def getSystem(self):
        return self._system
    
    # setters
    def setFormat(self, format):
        self._format = format

    def setVersion(self, version):
        self._version = version

    def setMeasurement(self, measurement):
        self._measurement = measurement

    def setSystem(self, system):
        self._system = system