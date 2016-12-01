

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

FOO = 'BAR'

def setmode(self, *args):
    pass


def cleanup():
    pass


# noinspection PyPep8Naming
def setwarnings(self, *args):
    pass


def setup(self, *args):
    pass


def add_event_detect(self, *args, **kwargs):
    pass


def add_event_callback(self, *args, **kwargs):
    pass


def output(self, *args, **kwargs):
    pass