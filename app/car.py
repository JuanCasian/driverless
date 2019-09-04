import sys
from threading import Timer
import time
import json
import os

class Car:
    config = {}

    speedA1 = None
    speedA2 = None
    speedB1 = None
    speedB2 = None
    duration = None

    timer_to_stop = None

    last_direction = None

    def __init__(self):
        self.initialize()

    def initialize(self):
        if Car.speedA1 is None or Car.speedB1 is None:
            try:
                from gpiozero import LED
                from aiy.pins import PIN_A
                from aiy.pins import PIN_B
                from aiy.pins import PIN_C
                from aiy.pins import PIN_D
                Car.speedA1 = LED(PIN_A)
                Car.speedA2 = LED(PIN_B)
                Car.speedB1 = LED(PIN_C)
                Car.speedB2 = LED(PIN_D)
                Car.connected = True
            except Exception as e:
                print(str(e))
                self.log('ERROR', 'Driving is not supported')
                Car.connected = False
        if len(Car.config.keys()) == 0:
            Car.load_config()

        return Car.connected

    @staticmethod
    def log(level, message):
        now = time.strftime('%d/%b/%y %H:%M:%S.{}'.format(str(time.time() % 1)[2:5]))
        print('{} - - [{}] {}'.format(level, now, message))

    @classmethod
    def load_config(cls):
        with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
            cls.config = json.load(f)

    def get_config(self):
        return Car.config

    @classmethod
    def _drive(cls, direction, canceling_last=False):
        if canceling_last:
            cls.timer_to_stop = None

        cls.log('INFO', 'Driving in direction "{}"'.format(direction))
        cls.speedA1.value = cls.config[direction]['speedA1']
        cls.speedA2.value = cls.config[direction]['speedA2']
        cls.speedB1.value = cls.config[direction]['speedB1']
        cls.speedB2.value = cls.config[direction]['speedB2']

    def drive(self, direction):
        if not self.initialize():
            return None

        if direction not in Car.config.keys():
            raise Exception('Direction "{}" not in {}'.format(direction, Car.config.keys()))

        # overwrite last direction
        if Car.timer_to_stop:
            Car.timer_to_stop.cancel()
            Car.timer_to_stop = None

        Car._drive(direction)

        # to go back the car first needs to stop
        if direction == 'back' and Car.last_direction != 'back':
            Timer(0.05, lambda: Car._drive('stop')).start()
            Timer(0.15, lambda: Car._drive(direction)).start()

        Car.last_direction = direction

        # stop after duration of driving
        if direction != 'stop':
            Car.timer_to_stop = Timer(Car.config[direction]['duration'],
                lambda: Car._drive('stop', canceling_last=True))
            Car.timer_to_stop.start()

            return Car.config[direction]['duration']

        return None
