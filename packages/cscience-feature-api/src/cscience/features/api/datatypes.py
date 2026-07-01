import inspect
import numpy as np


class DataTypeSpec:
    pass

class DataTypeId:

    types: list[type] = []

    def __init__(self):
        self.types.append(type(int))
        self.types.append(type(float))
        self.types.append(type(str))
        self.types.append(type(bool))
        self.types.append(type(np.ndarray))



    def __contains__(self, item):
        return item in self.__dict__