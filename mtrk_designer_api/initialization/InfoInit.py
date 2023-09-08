################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

class InfoInit:
    # constructor
    def __init__(self, *args):
        if len(args) == 6:
            self._description = args[0]
            self._slices = args[1]
            self._fov = args[2]
            self._pelines = args[3]
            self._seqstring = args[4]
            self._reconstruction = args[5]
        else:    
            self._description = "default"
            self._slices = 9999
            self._fov = 9999
            self._pelines = 9999
            self._seqstring = "default"
            self._reconstruction = "default"

    # getters
    def getDescription(self):
        return self._description
    
    def getSlices(self):
        return self._slices
    
    def getFov(self):
        return self._fov
    
    def getPeLines(self):
        return self._pelines
    
    def getSeqString(self):
        return self._seqstring
    
    def getReconstruction(self):
        return self._reconstruction
    
    # setters
    def setDescription(self, description):
        self._description = description

    def setSlices(self, slices):
        self._slices = slices

    def setFov(self, fov):
        self._fov = fov
    
    def setPeLines(self, pelines):
        self._pelines = pelines

    def setSeqString(self, seqstring):
        self._seqstring = seqstring

    def setReconstruction(self, reconstruction):
        self._reconstruction = reconstruction


    