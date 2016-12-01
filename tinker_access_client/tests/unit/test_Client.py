import unittest
from mock import patch, Mock

from tinker_access_client.tinker_access_client.ClientLogger import ClientLogger


class ClientTests(unittest.TestCase):

    @patch.object(ClientLogger, 'setup')
    def test____init__ConfiguresDevice(self, mock_setup):


        pass