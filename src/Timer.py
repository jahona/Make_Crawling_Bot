import timeit

class Timer():
    def __self__(self):
        self.__start = None
        self.__end = None

    def start(self):
        self.__start = timeit.default_timer()

    def end(self):
        self.__end = timeit.default_timer()

    def getTime(self):
        return self.__end - self.__start