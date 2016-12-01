import sys
from mock import Mock
from CustomImporter import CustomImporter


def setup_mock_logger():
    logger = Mock()
    logger.debug = Mock()
    logger.exception = Mock()
    return logger


def add_custom_importer():
    metas = sys.meta_path
    for meta in metas:
        if meta.__class__ is CustomImporter:
            sys.meta_path.remove(meta)
    sys.meta_path.append(CustomImporter())

# def import_device_modules():
#     import RPi
#     import lcdModule
#     import serial
#
#     return (Rpi, lcdModule, serial)