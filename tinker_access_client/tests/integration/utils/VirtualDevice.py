import os
import serial
import threading
from mock import patch

from tinker_access_client.tinker_access_client.State import State
from tinker_access_client.tinker_access_client.Client import Client
from tinker_access_client.tinker_access_client.ClientOption import ClientOption

from tinker_access_client.tests.integration.utils.VirtualRpi import VirtualRpi
from tinker_access_client.tests.integration.utils.VirtualSerial import VirtualSerial


class VirtualDevice(object):
    def __init__(self, opts):
        self.__opts = opts
        self.__virtual_serial = VirtualSerial()

        #TODO: should only patch if the address, matches the option for the serial address

        self.__serial_patcher = patch.object(serial, 'Serial', return_value=self.__virtual_serial)
        self.__serial_patcher.start()
        self.__rpi = VirtualRpi(opts)

    def __enter__(self):
        def run():
            Client.run(self.__opts, [])

        t = threading.Thread(target=run)
        t.daemon = True
        t.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__serial_patcher.stop()

    def status(self):
        status_file = self.__opts.get(ClientOption.STATUS_FILE)
        status = State.TERMINATED
        if os.path.isfile(status_file):
            with open(status_file, 'r') as f:
                status = f.readline().strip()

        return status

    def scan_badge(self, badge_code):
        self.__virtual_serial.scan_badge(badge_code)
