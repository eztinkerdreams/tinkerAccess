import logging
import webbrowser
from threading import Thread

from tinker_access_client.ClientLogger import ClientLogger
from virtual_device.VirtualDeviceServer import VirtualDeviceServer


class VirtualGPIO(object):
    # https://sourceforge.net/p/raspberry-gpio-python/code/ci/default/tree/source/c_gpio.h

    # define MODE_UNKNOWN -1
    # define BOARD        10
    # define BCM          11
    # define SERIAL       40
    # define SPI          41
    # define I2C          42
    # define PWM          43

    # define SETUP_OK           0
    # define SETUP_DEVMEM_FAIL  1
    # define SETUP_MALLOC_FAIL  2
    # define SETUP_MMAP_FAIL    3
    # define SETUP_CPUINFO_FAIL 4
    # define SETUP_NOT_RPI_FAIL 5

    # define INPUT  1 // is really 0 for control register!
    # define OUTPUT 0 // is really 1 for control register!
    # define ALT0   4

    # define PUD_OFF  0
    HIGH = 1
    LOW = 0
    BCM = 11
    IN = 0
    OUT = 1
    PUD_DOWN = 1
    PUD_UP = 2

    # TODO: confirm these values
    RISING = 1
    FALLING = 2
    BOTH = 3

    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__virtual_device_thread = Thread(target=VirtualDeviceServer.start)
        self.__virtual_device_thread.daemon = True
        self.__virtual_device_thread.start()

    def setmode(self, *args):
        pass

    def cleanup(self, *args):
        pass

    # noinspection PyPep8Naming
    def setwarnings(self, *args):
        pass

    def setup(self, *args):
        pass

    def add_event_detect(self, *args):
        pass

    def add_event_callback(self, *args):
        pass


# # noinspection PyClassHasNoInit
# class VirtualRPi:
#     GPIO = _VirtualGPIO()
#
# GPIO = _VirtualGPIO()
