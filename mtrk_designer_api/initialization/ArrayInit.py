################################################################################
### mtrk project - SDL file generator allowing to simply define MRI pulse    ###
### sequences that can be read by the mtrk project simulator and driver      ###
### sequence.                                                                ###
### Version 0.0.1                                                            ###
### Anais Artiges and the mtrk project team at NYU - 09/07/2023              ###
################################################################################

class ArrayInit:
    # constructor
    def __init__(self, *args):
        if len(args) == 4:
            self._encoding = args[0]
            self._type = args[1]
            self._size = args[2]
            self._data = args[3]
        else:    
            self._encoding = "default_encoding"
            self._type = "default_type"
            self._size = 9999
            self._data = []

    # getters
    def getEncoding(self):
        return self._encoding
    
    def getType(self):
        return self._type
    
    def getSize(self):
        return self._size
    
    def getData(self):
        return self._data
    

    # setters
    def setEncoding(self, encoding):
        self._encoding = encoding

    def setType(self, type):
        self._type = type

    def setSize(self, size):
        self._size = size
    
    def setData(self, data):
        self._data = data

    