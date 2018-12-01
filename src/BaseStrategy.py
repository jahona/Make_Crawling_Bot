import abc

class BaseStrategy(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @abc.abstractmethod
    def crawler(self):
        pass