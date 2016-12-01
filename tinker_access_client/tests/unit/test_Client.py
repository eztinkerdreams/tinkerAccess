import unittest
from mock import patch, Mock

from tinker_access_client.tinker_access_client.Client import Client, State
from tinker_access_client.tinker_access_client.DeviceApi import DeviceApi
from tinker_access_client.tinker_access_client.ClientLogger import ClientLogger


class ClientTests(unittest.TestCase):

    @patch.object(ClientLogger, 'setup')
    @patch.object(DeviceApi, '__new__')
    def test_runInitializesDevice(self, _0, _1):
        client = Client()
        self.assertEqual(client.state, State.INITIALIZED)