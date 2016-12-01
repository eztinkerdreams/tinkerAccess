import os
import unittest
from mock import Mock, patch

import logging
import logging.handlers

from tinker_access_client.tinker_access_client.ClientLogger import ClientLogger
from tinker_access_client.tinker_access_client.ClientOption import ClientOption
from tinker_access_client.tinker_access_client.ContextFilter import ContextFilter
from tinker_access_client.tinker_access_client.ClientOptionParser import ClientOptionParser


class TestClientLogger(unittest.TestCase):

    @patch.object(os, 'path')
    @patch.object(os, 'makedirs')
    @patch.object(logging, 'getLogger')
    @patch.object(logging, 'StreamHandler')
    @patch.object(ClientOptionParser, '__new__')
    @patch.object(logging.handlers, 'SysLogHandler')
    @patch.object(logging.handlers, 'TimedRotatingFileHandler')
    def test_setupSetsLogLevel(self, _0, _1, mock_parser, _3, _4, _5, mock_path):
        mock_path.exists.return_value = False
        log_level = 9
        mock_parser.return_value.parse_args.return_value = ({
            ClientOption.LOG_LEVEL: log_level
        }, [])
        logger = ClientLogger.setup()
        logger.setLevel.assert_called_with(9)

    @patch.object(os, 'path')
    @patch.object(os, 'makedirs')
    @patch.object(logging, 'getLogger')
    @patch.object(logging, 'StreamHandler')
    @patch.object(ClientOptionParser, '__new__')
    @patch.object(logging.handlers, 'SysLogHandler')
    @patch.object(logging.handlers, 'TimedRotatingFileHandler')
    @patch.object(ContextFilter, '__new__')
    @unittest.skip("temporarily disabled")
    def test_setupAddsContextFilter(self, mock_context_filter, _0, _1, mock_parser, _2, _3, _4, mock_path):
        mock_parser.return_value.parse_args.return_value = ({}, [])
        mock_path.exists.return_value = False
        logger = ClientLogger.setup()
        logger.addFilter.assert_called_with(mock_context_filter())

    @patch.object(os, 'path')
    @patch.object(os, 'makedirs')
    @patch.object(logging, 'getLogger')
    @patch.object(logging, 'StreamHandler')
    @patch.object(ClientOptionParser, '__new__')
    @patch.object(logging.handlers, 'SysLogHandler')
    @patch.object(logging.handlers, 'TimedRotatingFileHandler')
    @unittest.skip("temporarily disabled")
    def test_setupAddsSysLogHandler(self, _0, mock_sys_log_handler, mock_parser, _1, _2, mock_makedirs, mock_path):
        mock_parser.return_value.parse_args.return_value = ({}, [])
        mock_path.exists.return_value = True
        logger = ClientLogger.setup()
        mock_sys_log_handler.assert_any_call('/dev/log')
        logger.addHandler.assert_any_call(mock_sys_log_handler.return_value)

    @patch.object(os, 'path')
    @patch.object(os, 'makedirs')
    @patch.object(logging, 'getLogger')
    @patch.object(logging, 'StreamHandler')
    @patch.object(ClientOptionParser, '__new__')
    @patch.object(logging.handlers, 'SysLogHandler')
    @patch.object(logging.handlers, 'TimedRotatingFileHandler')
    def test_setupAddsStreamHandler(self, _0, _1, mock_parser, mock_stream_handler, _2, _3, mock_path):
        mock_parser.return_value.parse_args.return_value = ({}, [])
        mock_path.exists.return_value = False
        logger = ClientLogger.setup()
        logger.addHandler.assert_any_call(mock_stream_handler.return_value)

    @patch.object(os, 'path')
    @patch.object(os, 'makedirs')
    @patch.object(logging, 'getLogger')
    @patch.object(logging, 'StreamHandler')
    @patch.object(ClientOptionParser, '__new__')
    @patch.object(logging.handlers, 'SysLogHandler')
    @patch.object(logging.handlers, 'TimedRotatingFileHandler')
    def test_setupAddsTimedRotatingFileHandler(self, mock_file_handler, _0, mock_parser, _1, _2, mock_makedirs, mock_path):
        log_file = 'foo'
        mock_parser.return_value.parse_args.return_value = ({
            ClientOption.LOG_FILE: log_file
        }, [])
        mock_path.exists.return_value = False
        mock_path.dirname.return_value = log_file

        logger = ClientLogger.setup()
        mock_makedirs.assert_called_with(log_file)
        mock_file_handler.assert_called_with(log_file, when='D', interval=1, backupCount=7)
        logger.addHandler.assert_any_call(mock_file_handler.return_value)
