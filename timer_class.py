class Timer:
    """ Timer, that depends on ticks
        Attributes:
            self.active: bool
                to check if timer is running

        Methods:
            self.start( ticks )
                starts the timer
            self.update( ticks )
                update every tick
            self.stop()
                stops the timer
            self.reset()
                resets the timer

        """
    def __init__(self) -> None:
        self.__running: bool = False
        self.__start_time: int = 0
        self.__time: int = 0

    @property
    def active(self) -> bool:
        """ checks if timer is working """
        return self.__running

    def start(self, ticks: int) -> None:
        """ starts the timer """
        self.__start_time = ticks
        self.__running = True

    def update(self, ticks: int) -> None:
        """ should be put in the loop, update every frame """
        if self.__running:
            self.__time = ticks - self.__start_time

    def stop(self) -> None:
        """ stops the timer """
        self.__running = False

    def reset(self) -> None:
        """ resets the timer """
        self.__running = False
        self.__start_time = 0
        self.__time = 0

    @property
    def real_time(self) -> int:
        """ returns time in ticks """
        return self.__time

    @property
    def time(self) -> str:
        """ returns time in str xx:xx:xx """
        if self.__time > 0:
            human_time = self.__time // 1000
            minutes = human_time // 60
            seconds = human_time % 60
            milliseconds = (self.__time % 1000) // 10
            return f"{minutes:02}:{seconds:02}:{milliseconds:02}"
        return "00:00:00"