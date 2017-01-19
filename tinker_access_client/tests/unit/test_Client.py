import unittest
from mock import patch

from tinker_access_client.tinker_access_client.Client import Client, State
from tinker_access_client.tinker_access_client.DeviceApi import DeviceApi
from tinker_access_client.tinker_access_client.ClientLogger import ClientLogger
from tinker_access_client.tinker_access_client.ClientOptionParser import ClientOptionParser


class ClientTests(unittest.TestCase):

    @patch.object(ClientLogger, 'setup')
    @patch.object(DeviceApi, '__new__')
    @patch.object(ClientOptionParser, '__new__')
    def test_runInitializesDevice(self, _0, _1, _2):
        client = Client()
        self.assertEqual(client.state, State.INITIALIZED)