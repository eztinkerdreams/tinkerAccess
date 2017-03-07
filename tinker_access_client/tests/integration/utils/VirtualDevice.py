import os
import time
import serial
import threading
from mock import patch
from collections import deque

from tinker_access_client.tinker_access_client.State import State
from tinker_access_client.tinker_access_client.Client import Client
from tinker_access_client.tinker_access_client.ClientOption import ClientOption

from tinker_access_client.tests.integration.utils.VirtualRpi import VirtualRpi
from tinker_access_client.tests.integration.utils.VirtualSerial import VirtualSerial

update_status = Client.update_status


class VirtualDevice(object):

    def __init__(self, opts):
        self.__opts = opts
        self.__displays = []
        self.__client = None
        self.__transitions = []
        self.__virtual_serial = VirtualSerial()

        #TODO: should only patch if the address, matches the option for the serial address
        self.__serial_patcher = patch.object(serial, 'Serial', return_value=self.__virtual_serial)
        self.__serial_patcher.start()

        self.__client__update_status = patch.object(Client, 'update_status', side_effect=self.__update__status, autospec=True)
        self.__client__update_status.start()

        self.__rpi = VirtualRpi(opts)

    def __update__status(self, *args, **kwargs):
        self.__client = args[0]
        self.__transitions.append(self.__client.status())
        update_status(self.__client, *args, **kwargs)

    def __enter__(self):
        def run():
            Client.run(self.__opts, [])

        t = threading.Thread(target=run)
        t.daemon = True
        t.start()

        time.sleep(1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__serial_patcher.stop()
        self.__client__update_status.stop()

    def transitions(self):
        return self.__transitions

    def status(self):
        return self.__client.status() if self.__client is not None else None

    def scan_badge(self, badge_code):
        self.__virtual_serial.scan_badge(badge_code)
