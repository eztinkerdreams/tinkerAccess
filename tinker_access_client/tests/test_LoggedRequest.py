import unittest
from mock import patch, Mock

import requests as _request

from tinker_access_client.tests.utils import setup_mock_logger
from tinker_access_client.tinker_access_client.LoggedRequest import LoggedRequest as requests
from tinker_access_client.tinker_access_client.ClientLogger import ClientLogger


class LoggedRequestTest(unittest.TestCase):

    @patch.object(_request, 'get')
    @patch.object(ClientLogger, 'setup', return_value=setup_mock_logger())
    def test_getLogsRequest(self, mock_setup, mock_get):
        url = 'foo'
        params = ['a', 'b', 'c']
        kwargs = {'foo': 'bar'}
        requests.get(url, params, **kwargs)

        logger = mock_setup.return_value
        mock_get.assert_called_with(url, params, **kwargs)
        self.assertEqual(logger.debug.call_count, 3)

    @patch.object(_request, 'get')
    @patch.object(ClientLogger, 'setup', return_value=setup_mock_logger())
    def test_getRaisesExceptionOnInValidResponse(self, mock_setup, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = _request.RequestException()
        mock_get.return_value = mock_response

        logger = mock_setup.return_value
        self.assertRaises(_request.RequestException, requests.get, 'foo')
        self.assertEqual(logger.debug.call_count, 3)
        self.assertEqual(logger.exception.call_count, 1)

    @patch.object(_request, 'get', side_effect=RuntimeError)
    @patch.object(ClientLogger, 'setup', return_value=setup_mock_logger())
    def test_getLogsExceptions(self, mock_setup, _):
        self.assertRaises(RuntimeError, requests.get, 'foo')

        logger = mock_setup.return_value
        self.assertEqual(logger.debug.call_count, 2)
        self.assertEqual(logger.exception.call_count, 1)
