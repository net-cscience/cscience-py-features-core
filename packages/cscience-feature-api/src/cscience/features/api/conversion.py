from typing import Callable

class Convertors:
    pass

class ConversionRegistry:

    converters: dict[type, dict[tuple[type, type], Callable]]

    def __init__(self) -> None:
        '''
        Adds core converters
        '''
        pass

    def AddConverters(self, converters: Convertors) -> Convertors:
        '''
        Adds converters from another Convertors instance
        '''
        pass

    def AddConverter(self, converters: Callable) -> Convertors:
        '''
        Adds a convertion method
        '''
        pass
