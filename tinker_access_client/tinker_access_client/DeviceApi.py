import time
import json
import logging
import threading
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
        self.__fault = None
        self.__should_exit = False
        self.__edge_detected = False
        self.__logger = logging.getLogger(__name__)

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

    def __init__device_modules(self):
        self.__init_gpio()
        self.__init_lcd()
        self.__init__serial()

    def __init_gpio(self):
        try:
            import RPi.GPIO as GPIO

            # TODO: log print board info after init...
            # To discover information about your RPi:
            # GPIO.RPI_INFO
            # To discover the Raspberry Pi board revision:
            # GPIO.RPI_INFO['P1_REVISION']
            # GPIO.RPI_REVISION    (deprecated)
            # To discover the version of RPi.GPIO:
            # GPIO.VERSION

        except Exception as e:
            # try:
            #     import debug.VirtualRPi.VirtualGPIO as GPIO
            # except Exception as ex:
            #     # self.__logger.debug('Failed to patch RPi.GPIO module with virtual GPIO module.')
            #     # self.__logger.exception(ex)
            raise e

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__opts.get(ClientOption.PIN_LED_RED), GPIO.OUT)
        GPIO.setup(self.__opts.get(ClientOption.PIN_LED_BLUE), GPIO.OUT)
        GPIO.setup(self.__opts.get(ClientOption.PIN_LED_GREEN), GPIO.OUT)
        GPIO.setup(self.__opts.get(ClientOption.PIN_POWER_RELAY), GPIO.OUT)
        GPIO.setup(self.__opts.get(ClientOption.PIN_LOGOUT), GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(self.__opts.get(ClientOption.PIN_CURRENT_SENSE), GPIO.IN, GPIO.PUD_DOWN)
        self.GPIO = GPIO

    def __init_lcd(self):
        try:
            import lcdModule as LCD
        except Exception as e:
            try:
                import debug.VirtualLcd.VirtualLCD as LCD
            except Exception as ex:
                self.__logger.debug('Failed to patch lcdModule.LCD module with virtual LCD module.')
                self.__logger.exception(ex)
                raise e

        LCD.lcd_init()
        self.__LCD = LCD

    def __init__serial(self):
        serial_port_name = self.__opts.get(ClientOption.SERIAL_PORT_NAME)
        serial_port_speed = self.__opts.get(ClientOption.SERIAL_PORT_SPEED)

        try:
            import serial
            self.__serial_connection = serial.Serial(serial_port_name, serial_port_speed)

        except Exception as e:
            try:
                # noinspection PyPep8Naming
                from debug.VirtualSerial import VirtualSerial as serial
                self.__serial_connection = serial.Serial(serial_port_name, serial_port_speed)
            except Exception as ex:
                self.__logger.debug('Failed to patch serial module with virtual LCD module.')
                self.__logger.exception(ex)
                raise e

        self.__serial_connection.flushInput()
        self.__serial_connection.flushOutput()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__stop()
        self.__do_cleanup()

    def __stop(self):
        self.__should_exit = True

    def __do_cleanup(self):
        self.__write_to_lcd('System Offline!', "Try later...")
        self.GPIO.cleanup()

    def __do_callback(self, call_back, *args, **kwargs):
        try:
            call_back(*args, **kwargs)
        except Exception as e:
            self.__fault = e
            self.__stop()
        finally:
            self.__edge_detected = True

    def __poll_for_serial_input(self, call_back):
        while not self.__should_exit:
            try:
                badge_code = self.read(Channel.SERIAL)
                if badge_code:
                    self.__do_callback(call_back, badge_code=badge_code)
            except Exception as e:
                self.__fault = e
                self.__stop()
            time.sleep(.5)

    def __read_from_serial(self):
        serial_connection = self.__serial_connection

        if serial_connection.inWaiting() > 1:
            value = serial_connection.readline().strip()[-12:]
            serial_connection.flushInput()
            serial_connection.flushOutput()
            return value

        return None

    def __read_from_pin(self, pin, expected_state):
        # noinspection PyPep8Naming
        GPIO = self.GPIO
        expected_state = GPIO.LOW if not expected_state else GPIO.HIGH
        return GPIO.input(pin) == expected_state

    def __write_to_led(self, red, green, blue):
        # noinspection PyPep8Naming
        GPIO = self.GPIO
        GPIO.output(self.__opts.get(ClientOption.PIN_LED_RED), red)
        GPIO.output(self.__opts.get(ClientOption.PIN_LED_GREEN), green)
        GPIO.output(self.__opts.get(ClientOption.PIN_LED_BLUE), blue)

    def __write_to_lcd(self, first_line, second_line):
        # noinspection PyPep8Naming
        LCD = self.__LCD
        LCD.lcd_string(first_line, LCD.LCD_LINE_1)
        LCD.lcd_string(second_line, LCD.LCD_LINE_2)
        #time.sleep(2)

    def __write_to_pin(self, pin, state):
        # noinspection PyPep8Naming
        GPIO = self.GPIO
        state = GPIO.LOW if not state else GPIO.HIGH
        GPIO.output(pin, state)

    def on(self, channel, **kwargs):
        pin = kwargs.get('pin')
        direction = kwargs.get('direction')
        call_back = kwargs.get('call_back')

        # noinspection PyPep8Naming
        GPIO = self.GPIO
        if channel is Channel.PIN and pin and direction and call_back:

            def edge_detected(*args, **kwargs):
                self.__do_callback(call_back, args, kwargs)

            GPIO.add_event_detect(pin, direction, callback=edge_detected, bouncetime=250)

        elif channel is Channel.SERIAL and direction is self.GPIO.IN and call_back:
            poll_for_serial_input = threading.Thread(
                name='poll_for_serial_input',
                target=self.__poll_for_serial_input,
                args=(call_back,)
            )
            poll_for_serial_input.daemon = True
            poll_for_serial_input.start()

        else:
            raise NotImplementedError

    def read(self, channel, *args):
        if self.__should_exit:
            return

        channel_name = Channel(channel)
        try:

            if channel == Channel.SERIAL:
                value = self.__read_from_serial()

            elif channel == Channel.PIN:
                pin = args[0] if len(args) >= 1 else None
                expected_state = args[1] if len(args) >= 2 else True
                value = self.__read_from_pin(pin, expected_state)

            else:
                raise NotImplementedError

        except Exception as e:
            self.__logger.debug('Read from %s failed with args \'%s\'.', channel_name, args)
            self.__logger.exception(e)
            raise e

        return value

    def write(self, channel, *args):
        if self.__should_exit:
            return

        channel_name = Channel(channel)
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
                raise NotImplementedError

        except Exception as e:
            self.__logger.debug('Write to \'%s\' failed with args \'%s\'.', channel_name, args)
            self.__logger.exception(e)
            raise e

    def wait(self):
        while not self.__should_exit and not self.__edge_detected:
            time.sleep(1)
        self.__edge_detected = False
        self.__raise_fault()

    def __raise_fault(self):
        if self.__fault:
            raise self.__fault

