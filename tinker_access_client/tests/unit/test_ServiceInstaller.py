import os
import unittest
import subprocess
from mock import patch, Mock

from tinker_access_client.tinker_access_client.ClientLogger import ClientLogger
from tinker_access_client.tinker_access_client.ServiceInstaller import ServiceInstaller


class TestServiceInstaller(unittest.TestCase):

    @patch.object(os, 'chmod')
    @patch.object(subprocess, 'Popen')
    @patch.object(ClientLogger, 'setup')
    def test_installInvokesInstallScript(self, mock_setup, mock_popen, mock_chmod):
        install_lib = 'foo/'
        mock_install_process = Mock()
        mock_stdout_data = 'ok'
        mock_stderr_data = ''
        mock_install_process.returncode = 0
        mock_install_process.communicate.return_value = (mock_stdout_data, mock_stderr_data)
        mock_popen.return_value = mock_install_process
        ServiceInstaller.install(install_lib)

        mock_chmod.assert_any_call('{0}tinker_access_client/scripts/install.sh'.format(install_lib), 0755)
        mock_chmod.assert_any_call('{0}tinker_access_client/Service.py'.format(install_lib), 0755)

        logger = mock_setup.return_value
        self.assertEquals(logger.debug.call_count, 3)

    @patch.object(os, 'chmod')
    @patch.object(subprocess, 'Popen')
    @patch.object(ClientLogger, 'setup')
    def test_installRaisesExceptionOnInstallScriptError(self, mock_setup, mock_popen, _):
        mock_install_process = Mock()
        mock_stdout_data = 'doing something'
        mock_stderr_data = 'oh oh... something went wrong!'
        mock_install_process.returncode = 1  # Indicates an error occurred while executing the bash script
        mock_install_process.communicate.return_value = (mock_stdout_data, mock_stderr_data)
        mock_popen.return_value = mock_install_process

        self.assertRaises(RuntimeError, ServiceInstaller.install, '')

        logger = mock_setup.return_value
        logger.error.assert_called_with(mock_stderr_data)
        self.assertEqual(logger.exception.call_count, 1)

    @patch.object(os, 'chmod')
    @patch.object(ClientLogger, 'setup')
    def test_installLogsExceptions(self, mock_setup, mock_chmod):
        mock_chmod.side_effect = RuntimeError

        self.assertRaises(RuntimeError, ServiceInstaller.install, '')

        logger = mock_setup.return_value
        self.assertEquals(logger.debug.call_count, 1)
        self.assertEqual(logger.exception.call_count, 1)


