from unittest import TestCase

from mock import patch

from tinker_access_client.tinker_access_client.ClientLogger import ClientLogger
from tinker_access_client.tinker_access_client.TinkerAccessClient import TinkerAccessClient


# TODO: rename to client?
class TestTinkerAccessClient(TestCase):

    @patch.object(ClientLogger, 'setup')
    def test_runFoo(self, mock_logger):
        #TODO: implement
        pass

        # x = TinkerAccessClient().run()
        # self.assertTrue(x, None)
