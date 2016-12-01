import unittest

from mock import patch
from tinker_access_client.tinker_access_client.Service import run
from tinker_access_client.tinker_access_client.CommandHandler import CommandHandler


class TestDService(unittest.TestCase):

    @patch.object(CommandHandler, 'handle_command')
    def test_runReturnsCommandResult(self, handle_command):
        return_value = 'foo'
        handle_command.return_value = return_value
        self.assertEqual(run(), return_value)

    @patch.object(CommandHandler, 'handle_command')
    def test_runReturnsCommandResult(self, handle_command):
        handle_command.side_effect = ZeroDivisionError
        self.assertRaises(SystemExit, run)

