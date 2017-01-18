import time
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
            self.__init__device_modules()

        except (RuntimeError, ImportError) as e:
            self.__logger.exception(e)
            raise e

        except Exception as e:
            self.__logger.debug('Device initialization failed with %s.', json.dumps(opts, indent=4, sort_keys=True))
            self.__logger.exception(e)
            raise e

        self.__logger.debug('Device initialization succeeded.')

    # TODO: re-configure to use edge detection for signaling rather than polling
    # noinspection PyPep8Naming,PyUnresolvedReferences
    def __init__device_modules(self):

        try:
            import RPi.GPIO
            import lcdModule.LCD
            import serial
        except (RuntimeError, ImportError) as e:
            # If the above import fails it means this code is not executing on a physical RPi device.
            # so the modules are replaced with virtual modules for testing/development/debug purposes
            # this logic will probably get moved into a CustomImporter module eventually
            # see file://tinkerAccess/tinker_access_client/tests/README.md for more info
            try:
                from debug.VirtualRPi import VirtualRPi as RPi
                from debug.VirtualLcd import VirtualLcd as lcdModule
                from debug.VirtualSerial import VirtualSerial as serial
            except Exception as ex:
                self.__logger.debug('Failed to patch RPi device modules with virtual device modules.')
                self.__logger.exception(ex)
                raise e

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
        LCD = lcdModule.LCD
        LCD.lcd_init()
        self.__LCD = LCD

        serial_port_name = self.__opts.get(ClientOption.SERIAL_PORT_NAME)
        serial_port_speed = self.__opts.get(ClientOption.SERIAL_PORT_SPEED)
        self.__serial_connection = serial.Serial(serial_port_name, serial_port_speed)
        self.__serial_connection.flushInput()
        self.__serial_connection.flushOutput()

    ##TODO: add test for __enter__, __exit__

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        #do cleanup, logout coast down etc..

        logout_coast_time = self.__opts.get(ClientOption.LOGOUT_COAST_TIME)
        #wait for client state to be done, max wait time is logout coast time
        #while self.state != done..
        pass

    #def __del__(self):

    def wait_for_edge(self):
        # TODO: implement correctly with the virtual/mock device self.__GPIO.wait_for_edge()
        # needs to get list of all configufed channels and wireup the function
        #self.__GPIO.wait_for_edge()  # Blocks until next edge is detected

        time.sleep(1) #Remove once the above code is implemented to block correctly






    def write(self, channel, *args):
        channel_name = Channel(channel)
        self.__logger.debug('Attempting to write to \'%s\' with args %s...', channel_name, args)

        try:
            if channel == Channel.LED:
                red = len(args) >= 1 and args[0] is True
                green = len(args) >= 2 and args[1] is True
                blue = len(args) >= 3 and args[2] is True
                self.__write_to_led(red, green, blue)

            elif channel == Channel.LCD:
                first_line = args[0] if len(args) >= 1 else ''
                second_line = args[1] if len(args) >= 2 else ''
                self.__write_to_lcd(first_line, second_line)

            elif channel == Channel.PIN:
                pin = args[0] if len(args) >= 1 else None
                state = args[1] if len(args) >= 2 else None
                self.__write_to_pin(pin, state)

            else:
                raise NotImplemented

        except Exception as e:
            self.__logger.debug('Write to \'%s\' failed.', channel_name, args)
            self.__logger.exception(e)
            raise e

        self.__logger.debug('Write to \'%s\' succeeded.', channel_name)

    # noinspection PyPep8Naming
    def __write_to_led(self, red, green, blue):
        GPIO = self.__GPIO
        GPIO.output(self.__opts.get(ClientOption.PIN_LED_RED), red)
        GPIO.output(self.__opts.get(ClientOption.PIN_LED_GREEN), green)
        GPIO.output(self.__opts.get(ClientOption.PIN_LED_BLUE), blue)

    # noinspection PyPep8Naming
    def __write_to_lcd(self, first_line, second_line):
        LCD = self.__LCD
        LCD.lcd_string(first_line, LCD.LCD_LINE_1)
        LCD.lcd_string(second_line, LCD.LCD_LINE_2)

    # noinspection PyPep8Naming
    def __write_to_pin(self, pin, state):
        GPIO = self.__GPIO
        state = GPIO.LOW if not state else GPIO.HIGH
        GPIO.output(pin, state)

    def read(self, channel, *args):
        channel_name = Channel(channel)
        self.__logger.debug('Attempting to read from \'%s\' with \'%s\'...', channel_name, args)

        try:

            if channel == Channel.SERIAL:
                value = self.__read_from_serial()

            elif channel == Channel.PIN:
                pin = args[0] if len(args) >= 1 else None
                expected_state = args[1] if len(args) >= 2 else True
                value = self.__read_from_pin(pin, expected_state)

            else:
                raise NotImplemented

        except Exception as e:
            self.__logger.debug('Read from \'%s\' failed with args \'%s\'.', channel_name, args)
            self.__logger.exception(e)
            raise e

        if value is not None and value is not False:
            self.__logger.debug('Successfully read \'%s\' from \'%s\'.', value, channel_name)

        return value

    def __read_from_serial(self):
        serial_connection = self.__serial_connection

        if serial_connection.inWaiting() > 1:
            value = serial_connection.readline().strip()[-12:]
            serial_connection.flushInput()
            serial_connection.flushOutput()
            return value

        return None

    # noinspection PyPep8Naming
    def __read_from_pin(self, pin, expected_state):
        GPIO = self.__GPIO
        expected_state = GPIO.LOW if not expected_state else GPIO.HIGH
        return GPIO.input(pin) == expected_state
