from MockLcd import MockLcd
from MockRPi import MockRPi
from MockSerial import MockSerial


def is_rpi_module(full_name):
    return full_name.endswith('.RPi')


def is_lcd_module(full_name):
    return full_name.endswith('.lcdModule')


def is_serial_module(full_name):
    return full_name.endswith('.serial')


def is_device_module(full_name):
    return is_lcd_module(full_name) or is_rpi_module(full_name) or is_serial_module(full_name)


class CustomImporter(object):

    def find_module(self, full_name, _):
        if is_device_module(full_name):
            return self

        return None

    @staticmethod
    def load_module(full_name):

        if is_rpi_module(full_name):
            return MockRPi

        if is_lcd_module(full_name):
            return MockLcd

        if is_serial_module(full_name):
            return MockSerial

        raise ImportError(full_name)