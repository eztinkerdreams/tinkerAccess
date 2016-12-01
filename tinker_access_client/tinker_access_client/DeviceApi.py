import json
from ClientLogger import ClientLogger
from ClientOptionParser import ClientOption


class Channel(object):
    LCD, SERIAL, LED, PIN = range(0, 4)

    def __new__(cls, channel):
        for key, value in vars(Channel).items():
            if not key.startswith('__'):
                if value == channel:
                    return key
        return None


class DeviceApi(object):
    def __init__(self, opts):
        self.__opts = opts
        self.__logger = ClientLogger.setup()
        self.__logger.debug('Attempting device initialization...')
        try:

            # !Important: These modules are imported locally at runtime so that the unit test
            # can run on non-rpi devices where GPIO won't load and cannot work
            # (i.e. the build server, and dev environments) see: test_DeviceApi.py

            self.__init__GPIO()
            self.__init__LCD()
            self.__init__SERIAL()

        except ImportError as e:
            self.__logger.error('RPi modules will only load from a physical RPi device. \n'
                                'Use the --debug flag to simulate RPi modules (i.e. GPIO) for development/testing')
            self.__logger.exception(e)
            raise e

        except Exception as e:
            self.__logger.debug('Device initialization failed with %s.', json.dumps(opts, indent=4, sort_keys=True))
            self.__logger.exception(e)
            raise e

        self.__logger.debug('Device initialization succeeded.')

    # TODO: re-configure to use edge detection for signaling rather than polling
    def __init__GPIO(self):
        import RPi

        GPIO = RPi.GPIO
        GPIO.setmode(GPIO.BCM)

        # TODO: remove once lcdModule is fixed fixed to not also call cleanup
        GPIO.cleanup()
        GPIO.setWarnings(False)

        GPIO.setup(self.__opts.get(ClientOption.PIN_LED_RED), GPIO.OUT)
        GPIO.setup(self.__opts.get(ClientOption.PIN_LED_BLUE), GPIO.OUT)
        GPIO.setup(self.__opts.get(ClientOption.PIN_LED_GREEN), GPIO.OUT)
        GPIO.setup(self.__opts.get(ClientOption.PIN_POWER_RELAY), GPIO.OUT)
        GPIO.setup(self.__opts.get(ClientOption.PIN_LOGOUT), GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(self.__opts.get(ClientOption.PIN_CURRENT_SENSE), GPIO.IN, GPIO.PUD_DOWN)
        self.__GPIO = GPIO

    # TODO: lcdModule needs some love... I'll come back to this later can probably just completely remove it.
    def __init__LCD(self):
        import lcdModule

        LCD = lcdModule.LCD
        LCD.lcd_init()
        self.__LCD = LCD

    def __init__SERIAL(self):
        import serial

        serial_port_name = self.__opts.get(ClientOption.SERIAL_PORT_NAME)
        serial_port_speed = self.__opts.get(ClientOption.SERIAL_PORT_SPEED)
        self.__SERIAL_CONNECTION = serial.Serial(serial_port_name, serial_port_speed)
        self.__SERIAL_CONNECTION.flushInput()
        self.__SERIAL_CONNECTION.flushOutput()

    def write(self, channel, *args):
        channel_name = Channel(channel)
        self.__logger.debug('Attempting to write to \'%s\' with args %s...', channel_name, args)

        try:
            if channel == Channel.LED:
                red = len(args) >= 1 and args[0] is True
                green = len(args) >= 2 and args[1] is True
                blue = len(args) >= 3 and args[2] is True
                self.__writeToLed(red, green, blue)

            elif channel == Channel.LCD:
                firstLine = args[0] if len(args) >= 1 else ''
                secondLine = args[1] if len(args) >= 2 else ''
                self.__writeToLcd(firstLine, secondLine)

            elif channel == Channel.PIN:
                pin = args[0] if len(args) >= 1 else None
                state = args[1] if len(args) >= 2 else None
                self.__writeToPin(pin, state)

            else:
                raise NotImplemented

        except Exception as e:
            self.__logger.debug('Write to \'%s\' failed.', channel_name, args)
            self.__logger.exception(e)
            raise e

        self.__logger.debug('Write to \'%s\' succeeded.', channel_name)

    def __writeToLed(self, red, green, blue):
        GPIO = self.__GPIO
        GPIO.output(self.__opts.get(ClientOption.PIN_LED_RED), red)
        GPIO.output(self.__opts.get(ClientOption.PIN_LED_GREEN), green)
        GPIO.output(self.__opts.get(ClientOption.PIN_LED_BLUE), blue)

    def __writeToLcd(self, firstLine, secondLine):
        LCD = self.__LCD
        LCD.lcd_string(firstLine, LCD.LCD_LINE_1)
        LCD.lcd_string(secondLine, LCD.LCD_LINE_2)

    def __writeToPin(self, pin, state):
        GPIO = self.__GPIO
        state = GPIO.LOW if not state else GPIO.HIGH
        GPIO.output(pin, state)

    def read(self, channel, *args):
        channel_name = Channel(channel)
        self.__logger.debug('Attempting to read from \'%s\' with \'%s\'...', channel_name, args)

        try:

            if channel == Channel.SERIAL:
                value = self.__readFromSerial()

            elif channel == Channel.PIN:
                pin = args[0] if len(args) >= 1 else None
                expectedState = args[1] if len(args) >= 2 else True
                value = self.__readFromPin(pin, expectedState)

            else:
                raise NotImplemented

        except Exception as e:
            self.__logger.debug('Read from \'%s\' failed with args \'%s\'.', channel_name, args)
            self.__logger.exception(e)
            raise e

        if value is not None and value is not False:
            self.__logger.debug('Successfully read \'%s\' from \'%s\'.', value, channel_name)

        return value

    def __readFromSerial(self):
        SERIAL_CONNECTION = self.__SERIAL_CONNECTION

        if SERIAL_CONNECTION.inWaiting() > 1:
            value = SERIAL_CONNECTION.readline().strip()[-12:]
            SERIAL_CONNECTION.flushInput()
            SERIAL_CONNECTION.flushOutput()
            return value

        return None

    def __readFromPin(self, pin, expectedState):
        GPIO = self.__GPIO
        expectedState = GPIO.LOW if not expectedState else GPIO.HIGH
        return GPIO.input(pin) == expectedState
