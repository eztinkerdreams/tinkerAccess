import unittest
from mock import patch

from tinker_access_client.tinker_access_client.Service import run
from tinker_access_client.tinker_access_client.ClientLogger import ClientLogger
from tinker_access_client.tinker_access_client.ClientDaemon import ClientDaemon
from tinker_access_client.tinker_access_client.ClientOptionParser import ClientOptionParser


#TODO: mock CommandHandler, and implement remaining unit test

class TestSetup(unittest.TestCase):

    @patch.object(ClientLogger, 'setup')
    @patch.object(ClientDaemon, 'start')
    @patch.object(ClientOptionParser, '__new__')
    def test_runHandlesStartCommand(self, mock_parser, mock_start, mock_setup):
        mock_parser.return_value.parse_args.return_value = ({}, ['start'])
        run()

        logger = mock_setup.return_value
        self.assertTrue(mock_start.call_count, 1)
        self.assertTrue(logger.debug.call_count, 1)

