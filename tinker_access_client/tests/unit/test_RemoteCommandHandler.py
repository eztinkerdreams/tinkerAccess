import sys
import unittest
from mock import patch

from tinker_access_client.tinker_access_client.ClientDaemon import ClientDaemon
from tinker_access_client.tinker_access_client.ClientLogger import ClientLogger
from tinker_access_client.tinker_access_client.ClientOptionParser import ClientOptionParser
from tinker_access_client.tinker_access_client.RemoteCommandHandler import RemoteCommandHandler

@unittest.skip("temporarily disabled")
class TestRemoteCommandHandler(unittest.TestCase):
    @patch.object(ClientLogger, 'setup')
    @patch.object(ClientOptionParser, '__new__')
    @patch.object(ClientDaemon, 'start')
    def test_startCommand(self, _, mock_parser, mock_setup):
        mock_parser.return_value.parse_args.return_value = ({}, ['start'])
        with RemoteCommandHandler() as handler:
            handler.wait()
            print 'bar'

        logger = mock_setup.return_value
        self.assertEqual(ClientDaemon.start.call_count, 1)
        self.assertEqual(logger.debug.call_count, 1)