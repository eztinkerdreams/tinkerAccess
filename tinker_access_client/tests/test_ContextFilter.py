import socket
import unittest

from tinker_access_client.tinker_access_client.PackageInfo import PackageInfo
from tinker_access_client.tinker_access_client.ClientOption import ClientOption
from tinker_access_client.tinker_access_client.ContextFilter import ContextFilter

device_id = 'some_device'


class TestContextFilter(unittest.TestCase):
    def setUp(self):
        ContextFilter({
            ClientOption.DEVICE_ID: device_id
        }).filter(record=self)

    def test_filter(self):
        self.assertTrue(self.device_id == device_id)
        self.assertTrue(self.version == PackageInfo.version)
        self.assertTrue(self.hostname == socket.gethostname())
        self.assertTrue(self.app_id == PackageInfo.pip_package_name)

        # TODO: user_id, badge_id etc...
