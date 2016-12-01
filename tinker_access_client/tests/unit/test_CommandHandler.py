import logging
import unittest

from mock import patch
from tinker_access_client.tinker_access_client.ClientOption import ClientOption
from tinker_access_client.tinker_access_client.ClientOptionParser import Command
from tinker_access_client.tinker_access_client.CommandHandler import CommandHandler

some_opts = {
    ClientOption.DEVICE_ID: 'someDevice'
}
some_args = [
    Command.START.get('command')
]


def some_function(opts=None, args=None):
    return opts, args


# noinspection PyUnusedLocal
def some_other_function(opts=None, args=None):
    raise ZeroDivisionError


class TestCommandHandler(unittest.TestCase):

    def test_handlesCommand(self):
        with CommandHandler(some_opts, some_args) as handler:
            handler.on(Command.START, some_function)
            self.assertEqual(
                handler.handle_command(),
                some_function(some_opts, some_args)
            )

    @patch.object(logging, 'getLogger')
    def test_handleCommandLogsAndRaisesUnexpectedException(self, mock_get):
        with CommandHandler(some_opts, some_args) as handler:
            handler.on(Command.START, some_other_function)
            self.assertRaises(ZeroDivisionError, handler.handle_command)
            logger = mock_get.return_value
            self.assertEqual(logger.debug.call_count, 1)
            self.assertEqual(logger.exception.call_count, 1)