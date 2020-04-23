from abc import ABC, abstractmethod
import time
import random
import multiprocessing
import logging

logging.basicConfig(filename='flight.log', level=logging.DEBUG)


class Event(ABC):
    def __init__(self, change_rate=1):
        self.change_rate = change_rate
        super().__init__()

    @abstractmethod
    def get_value(self):
        pass


class Turbulence(Event):
    def get_value(self):
        return random.gauss(0, self.change_rate)


class Correction(Event):
    def get_value(self):
        return self.change_rate


class Periodical:
    def __init__(self, period=360, start_val=0):
        self.period = period
        self.value = start_val

    def __setattr__(self, name, value):
        if name == "value":
            self.__dict__[name] = value % self.period
        elif name == "period":
            if value == 0:
                raise AttributeError("Period cannot be set to 0")
            self.__dict__[name] = value
        else:
            self.__dict__[name] = value


class Plane:
    def __init__(self, starting_tilt=0, correction_rate=1, name=''):
        self.tilt = Periodical(period=360, start_val=starting_tilt)
        self.correction = Correction(correction_rate)
        self.name = name

    def tilt_left(self):
        self.tilt.value -= self.correction.get_value()

    def tilt_right(self):
        self.tilt.value += self.correction.get_value()

    def tilt_report(self):
        return '{} Tilt: {:.3f}'.format(self.name, self.tilt.value)

    def is_left_tilted(self):
        return True if self.tilt.value >= 180 else False

    def is_right_tilted(self):
        return True if 0 < self.tilt.value < 180 else False

    def adjust_tilt(self):
        if self.tilt.value == 0:
            pass
        elif abs(self.tilt.value) < self.correction.get_value():
            logging.debug('slight tilt detected, leveling out...')
            self.tilt.value = 0
        elif self.is_right_tilted():
            logging.debug('right tilt detected, tilting LEFT...')
            self.tilt_left()
        elif self.is_left_tilted():
            logging.debug('left tilt detected, tilting RIGHT...')
            self.tilt_right()


def flight_step_generator(plane, ticks_for_turbulence=1.0, time_tick=1.0, turbulence_rate=0):
    n_ticks = 0
    turbulence = Turbulence(turbulence_rate)
    try:
        while True:
            if turbulence_rate != 0 and n_ticks % ticks_for_turbulence == 0.0:
                plane.tilt.value += turbulence.get_value()
            plane.adjust_tilt()
            logging.info(plane.tilt_report())
            print(plane.tilt_report())
            time.sleep(time_tick)
            n_ticks += 1
            yield n_ticks
    except KeyboardInterrupt:
        gen_message = "-----------------Flight of '{}' Interrupted-----------------".format(plane.name)
        print(gen_message)
        logging.debug(gen_message)


def simulate(step_generator, **kwargs):
    for tick in step_generator(**kwargs):
        pass


if __name__ == '__main__':
    try:
        first_plane = Plane(name='first', correction_rate=2)
        second_plane = Plane(name='second', correction_rate=3)
        first = multiprocessing.Process(target=simulate, kwargs={
            'step_generator': flight_step_generator,
            'plane': first_plane,
            'time_tick': 1.0,
            'ticks_for_turbulence': 5.0,
            'turbulence_rate': 15
        })
        second = multiprocessing.Process(target=simulate, kwargs={
            'step_generator': flight_step_generator,
            'plane': second_plane,
            'time_tick': 0.4,
            'ticks_for_turbulence': 4.0,
            'turbulence_rate': 15
        })

        first.start()
        second.start()

        first.join()
        second.join()

    except KeyboardInterrupt:
        main_message = "-----------------Program Interrupted-----------------"
        print(main_message)
        logging.debug(main_message)
