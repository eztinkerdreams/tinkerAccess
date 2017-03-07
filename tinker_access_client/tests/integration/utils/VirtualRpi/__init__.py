import sys
import RPi


def is_rpi_module(full_name):
    return full_name.endswith('.RPi')


def is_gpio_module(full_name):
    return full_name.endswith('.GPIO')


def is_lcd_module(full_name):
    return full_name.endswith('.lcdModule')


def is_lcd(full_name):
    return full_name.endswith('.LCD')


def is_serial_module(full_name):
    return full_name.endswith('.serial')


def is_device_module(full_name):
    return is_rpi_module(full_name) or is_gpio_module(full_name)


class VirtualRpi(object):

    def __init__(self, opts):
        self.__opts = opts
        self.__add_to_sys_path()

    def __del__(self):
        self.__remove_from_sys_path()

    def __remove_from_sys_path(self):
        [sys.meta_path.remove(meta) for meta in sys.meta_path if meta.__class__ is self.__class__]

    def __add_to_sys_path(self):
        self.__remove_from_sys_path()
        sys.meta_path.append(self)

    def find_module(self, full_name, _):
        if is_device_module(full_name):
            return self

        return None

    @staticmethod
    def load_module(full_name):
        if is_rpi_module(full_name):
            return RPi

        if is_gpio_module(full_name):
            return RPi.GPIO

        raise ImportError(full_name)
