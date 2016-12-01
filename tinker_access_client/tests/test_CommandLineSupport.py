import unittest
from mock import Mock, patch
from tinker_access_client.tinker_access_client.CommandLineSupport import run
from tinker_access_client.tinker_access_client.TinkerAccessClient import TinkerAccessClient


class TestCommandLineSupport(unittest.TestCase):

    @patch.object(TinkerAccessClient, '__new__')
    def test_runCreatesAndRunsTinkerAccessClient(self, mock_tinker_access_client):
        run()
        mock_tinker_access_client.return_value.run.assert_any_call()