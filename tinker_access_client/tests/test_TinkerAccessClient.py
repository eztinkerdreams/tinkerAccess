import unittest
from mock import Mock, patch

from tinker_access_client.tinker_access_client.ClientDaemon import ClientDaemon
from tinker_access_client.tinker_access_client.ClientLogger import ClientLogger
from tinker_access_client.tinker_access_client.ClientOptionParser import ClientOptionParser
from tinker_access_client.tinker_access_client.TinkerAccessClient import TinkerAccessClient


class TestTinkerAccessClient(unittest.TestCase):

    @patch.object(ClientLogger, 'setup')
    @patch.object(ClientDaemon, '__new__')
    @patch.object(ClientOptionParser, '__new__')
    def test_startDaemon(self, mock_parser, mock_daemon, mock_setup):
        pass
        # mock_parser.return_value.parse_args.return_value = ({}, ['start'])
        # TinkerAccessClient.run()
        #
        # logger = mock_setup.return_value
        # self.assertEqual(mock_daemon.start.call_count, 1)
        # self.assertEqual(logger.debug.call_count, 1)
        # pass

