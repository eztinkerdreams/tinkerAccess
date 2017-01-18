import sys
import unittest
from mock import Mock, patch
from tinker_access_client.tinker_access_client.ClientLogger import ClientLogger
from tinker_access_client.tinker_access_client.DeviceApi import DeviceApi, Channel
from tinker_access_client.tinker_access_client.ClientOptionParser import ClientOption
from tinker_access_client.tests.utils.CustomImporter import CustomImporter, add_custom_importer, is_device_module

mode_bcm = 11
pin_power_relay = 17
pin_logout = 16
pin_led_red = 21
pin_led_blue = 20
pin_led_green = 19
pin_current_sense = 12
serial_port_name = '/dev/ttyUSB0'
serial_port_speed = 9600

## TODO: add test for __enter__, __exit__ & refactor to use context sytanx in these test with Device() as device etc..


# noinspection PyUnresolvedReferences,PyPep8Naming,PyShadowingNames
class DeviceApiTests(unittest.TestCase):
    def setUp(self):
        add_custom_importer()
        self.__opts = {
            ClientOption.SERIAL_PORT_NAME: serial_port_name,
            ClientOption.SERIAL_PORT_SPEED: serial_port_speed,
            ClientOption.PIN_POWER_RELAY: pin_power_relay,
            ClientOption.PIN_LOGOUT: pin_logout,
            ClientOption.PIN_CURRENT_SENSE: pin_current_sense,
            ClientOption.PIN_LED_RED: pin_led_red,
            ClientOption.PIN_LED_GREEN: pin_led_green,
            ClientOption.PIN_LED_BLUE: pin_led_blue
        }

    def tearDown(self):
        # Replaces the mocks on the device modules so there is not test bleed
        for (k, m) in sys.modules.items():
            if is_device_module(k):
                for (p, v) in vars(m).items():
                    if isinstance(v, Mock):
                        setattr(m, p, Mock())

    @patch.object(ClientLogger, 'setup')
    def test__init__ConfiguresDevice(self, mock_setup):
        DeviceApi(self.__opts)

        import RPi.GPIO
        GPIO = RPi.GPIO
        GPIO.setmode.assert_any_call(GPIO.BCM)

        # # TODO: remove once lcdModule has been refactored
        GPIO.cleanup.assert_any_call()
        GPIO.setWarnings.assert_any_call(False)

        GPIO.setup.assert_any_call(pin_logout, GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup.assert_any_call(pin_current_sense, GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup.assert_any_call(pin_power_relay, GPIO.OUT)
        GPIO.setup.assert_any_call(pin_led_red, GPIO.OUT)
        GPIO.setup.assert_any_call(pin_led_green, GPIO.OUT)
        GPIO.setup.assert_any_call(pin_led_blue, GPIO.OUT)

        import lcdModule
        LCD = lcdModule.LCD
        LCD.lcd_init.assert_any_call()

        import serial
        serial_connection = serial.Serial.return_value
        serial.Serial.assert_any_call(serial_port_name, serial_port_speed)
        self.assertEqual(serial_connection.flushInput.call_count, 1)
        self.assertEqual(serial_connection.flushOutput.call_count, 1)

        logger = mock_setup.return_value
        self.assertEqual(logger.debug.call_count, 2)

    @patch.object(ClientLogger, 'setup')
    @patch.object(CustomImporter, 'load_module')
    def test__init__RaisesUnexpectedExceptions(self, mock_load_module, mock_setup):
        mock_load_module.side_effect = ZeroDivisionError

        self.assertRaises(ZeroDivisionError, DeviceApi, self.__opts)

        logger = mock_setup.return_value
        self.assertEqual(logger.debug.call_count, 2)
        self.assertEqual(logger.exception.call_count, 1)

    @unittest.skip('this test fails on travis-ci, need to figure out what the issue is')
    @patch.object(ClientLogger, 'setup')
    @patch.object(CustomImporter, 'load_module')
    def test__init__RaisesImportError(self, mock_load_module, mock_setup):
        mock_load_module.side_effect = ImportError

        self.assertRaises(ImportError, DeviceApi, self.__opts)

        logger = mock_setup.return_value
        self.assertEqual(logger.debug.call_count, 2)
        self.assertEqual(logger.exception.call_count, 2)

    @unittest.skip('this test fails on travis-ci, need to figure out what the issue is')
    @patch.object(ClientLogger, 'setup')
    @patch.object(CustomImporter, 'load_module')
    def test__init__RaisesRuntimeError(self, mock_load_module, mock_setup):
        mock_load_module.side_effect = RuntimeError

        self.assertRaises(RuntimeError, DeviceApi, self.__opts)

        logger = mock_setup.return_value
        self.assertEqual(logger.debug.call_count, 2)
        self.assertEqual(logger.exception.call_count, 2)

    @patch.object(ClientLogger, 'setup')
    def test_writeLogsOutput(self, mock_setup):
        device_api = DeviceApi(self.__opts)
        mock_setup.return_value.reset_mock()

        device_api.write(Channel.LED, True, False, False)

        logger = mock_setup.return_value
        self.assertEqual(logger.debug.call_count, 2)

    @patch.object(ClientLogger, 'setup')
    def test_writeRaisesUnexpectedExceptions(self, mock_setup):
        import RPi.GPIO
        RPi.GPIO.output.side_effect = RuntimeError
        deviceApi = DeviceApi(self.__opts)
        mock_setup.return_value.reset_mock()

        self.assertRaises(RuntimeError, deviceApi.write, Channel.LED)

        logger = mock_setup.return_value
        self.assertEqual(logger.debug.call_count, 2)
        self.assertEqual(logger.exception.call_count, 1)

    @patch.object(ClientLogger, 'setup')
    def test_writeToRedLed(self, _):
        device_api = DeviceApi(self.__opts)
        device_api.write(Channel.LED, True, False, False)

        import RPi.GPIO
        GPIO = RPi.GPIO
        GPIO.output.assert_any_call(pin_led_red, True)
        GPIO.output.assert_any_call(pin_led_green, False)
        GPIO.output.assert_any_call(pin_led_blue, False)

    @patch.object(ClientLogger, 'setup')
    def test_writeToGreenLed(self, _):
        deviceApi = DeviceApi(self.__opts)
        deviceApi.write(Channel.LED, False, True, False)

        import RPi.GPIO
        GPIO = RPi.GPIO
        GPIO.output.assert_any_call(pin_led_red, False)
        GPIO.output.assert_any_call(pin_led_green, True)
        GPIO.output.assert_any_call(pin_led_blue, False)

    @patch.object(ClientLogger, 'setup')
    def test_writeToBlueLed(self, _):
        deviceApi = DeviceApi(self.__opts)
        deviceApi.write(Channel.LED, False, False, True)

        import RPi.GPIO
        GPIO = RPi.GPIO
        GPIO.output.assert_any_call(pin_led_red, False)
        GPIO.output.assert_any_call(pin_led_green, False)
        GPIO.output.assert_any_call(pin_led_blue, True)

    @patch.object(ClientLogger, 'setup')
    def test_writeToPinAcceptsNumericValues(self, _):
        device_api = DeviceApi(self.__opts)

        import RPi.GPIO
        GPIO = RPi.GPIO
        device_api.write(Channel.PIN, pin_power_relay, GPIO.HIGH)
        GPIO.output.assert_any_call(pin_power_relay, True)
        GPIO.output.reset_mock()

        device_api.write(Channel.PIN, pin_power_relay, GPIO.LOW)
        GPIO.output.assert_any_call(pin_power_relay, False)

    @patch.object(ClientLogger, 'setup')
    def test_writeToPinAcceptsBooleanValues(self, _):
        device_api = DeviceApi(self.__opts)

        import RPi.GPIO
        GPIO = RPi.GPIO
        device_api.write(Channel.PIN, pin_power_relay, True)
        GPIO.output.assert_any_call(pin_power_relay, True)
        GPIO.output.reset_mock()

        device_api.write(Channel.PIN, pin_power_relay, False)
        GPIO.output.assert_any_call(pin_power_relay, False)

    @patch.object(ClientLogger, 'setup')
    def test_readRaisesUnexpectedExceptions(self, mock_setup):
        device_api = DeviceApi(self.__opts)
        mock_setup.return_value.reset_mock()

        import RPi.GPIO
        GPIO = RPi.GPIO
        GPIO.input.side_effect = RuntimeError
        self.assertRaises(RuntimeError, device_api.read, Channel.PIN, pin_logout)

        logger = mock_setup.return_value
        self.assertEqual(logger.debug.call_count, 2)
        self.assertEqual(logger.exception.call_count, 1)

    @patch.object(ClientLogger, 'setup')
    def test_readPinReturnsTrueWhenInputMatchesExpectedState(self, mock_setup):
        device_api = DeviceApi(self.__opts)
        logger = mock_setup.return_value
        logger.reset_mock()

        import RPi.GPIO
        GPIO = RPi.GPIO
        GPIO.input.return_value = GPIO.HIGH
        self.assertEqual(device_api.read(Channel.PIN, pin_logout), True)
        self.assertEqual(logger.debug.call_count, 2)
        logger.reset_mock()

        GPIO.input.return_value = GPIO.LOW
        self.assertEqual(device_api.read(Channel.PIN, pin_logout, False), True)
        self.assertEqual(logger.debug.call_count, 2)

    @patch.object(ClientLogger, 'setup')
    def test_readSerialReturnsValueAndLogsInput(self, mock_setup):
        device_api = DeviceApi(self.__opts)
        mock_setup.return_value.reset_mock()

        import serial
        serial.Serial.return_value.reset_mock()

        serial_connection = serial.Serial.return_value
        serial_connection.inWaiting.return_value = 2
        serial_connection.readline.return_value = 'X:foooooooobar'
        self.assertEqual(device_api.read(Channel.SERIAL), 'foooooooobar')
        self.assertEqual(serial_connection.flushInput.call_count, 1)
        self.assertEqual(serial_connection.flushOutput.call_count, 1)

        logger = mock_setup.return_value
        self.assertEqual(logger.debug.call_count, 2)

    @patch.object(ClientLogger, 'setup')
    def test_readSerialRaisesUnexpectedExceptions(self, mock_setup):
        device_api = DeviceApi(self.__opts)
        mock_setup.return_value.reset_mock()

        import serial
        serial_connection = serial.Serial.return_value
        serial_connection.inWaiting.side_effect = RuntimeError

        self.assertRaises(RuntimeError, device_api.read, Channel.SERIAL)

        logger = mock_setup.return_value
        self.assertEqual(logger.debug.call_count, 2)
        self.assertEqual(logger.exception.call_count, 1)

    @patch.object(ClientLogger, 'setup')
    def test_writeToLcd(self, _):
        device_api = DeviceApi(self.__opts)

        first_string = 'foo'
        second_string = 'bar'
        device_api.write(Channel.LCD, first_string, second_string)

        import lcdModule.LCD
        LCD = lcdModule.LCD
        LCD.lcd_string.assert_any_call(first_string, LCD.LCD_LINE_1)
        LCD.lcd_string.assert_any_call(second_string, LCD.LCD_LINE_2)
