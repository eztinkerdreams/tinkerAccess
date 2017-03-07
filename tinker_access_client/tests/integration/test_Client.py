from __future__ import absolute_import

import os
import time
import tempfile
import threading
import unittest
import requests
from mock import patch, Mock
from backports import tempfile

from tinker_access_client.tinker_access_client.State import State
from tinker_access_client.tinker_access_client.Client import Client
from tinker_access_client.tinker_access_client.PackageInfo import PackageInfo
from tinker_access_client.tinker_access_client.ClientOption import ClientOption
from tinker_access_client.tinker_access_client.ClientOptionParser import ClientOptionDefaults

from tinker_access_client.tests.integration.utils.VirtualDevice import VirtualDevice


def get_default_opts(temp_dir, opts=None):
    default_opts = ClientOptionDefaults.copy()
    default_opts.update({
        ClientOption.DEBUG: True,
        ClientOption.LOG_LEVEL: 10,
        ClientOption.PID_FILE: '{0}/{1}.pid'.format(temp_dir, PackageInfo.pip_package_name),
        ClientOption.LOG_FILE: '{0}/{1}.log'.format(temp_dir, PackageInfo.pip_package_name),
        ClientOption.CONFIG_FILE: '{0}/{1}.conf'.format(temp_dir, PackageInfo.pip_package_name),
        ClientOption.STATUS_FILE: '{0}/{1}.status'.format(temp_dir, PackageInfo.pip_package_name),
        ClientOption.LOGGING_CONFIG_FILE: '{0}/{1}.logging.conf'.format(temp_dir, PackageInfo.pip_package_name)
    })
    default_opts.update(opts or {})
    return default_opts


def get_state(opts):
    status_file = opts.get(ClientOption.STATUS_FILE)
    status = terminated = State.TERMINATED
    if os.path.isfile(status_file):
        with open(status_file, 'r') as f:
            status = f.readline().strip()

    return status if status is not terminated else None


def wait_for_state(opts, state, max_wait_time=1):
    current = time.time()
    while get_state(opts) != state and time.time() - current < max_wait_time:
        time.sleep(0.1)
    return get_state(opts)


#TODO: add test, should read from config file ( can test by writting config file to temp_dir)
#TODOL add test should use logging config etc...( can test by writting config file to temp_dir)

#TODO: graceful exit test will need to mock out the function ClientDaemon__get_process_ids,
#since the signature is wrong of the process is wrong...


user_id = 'someUserId'
session_seconds = 60
device_id = 'someDevice'
remaining_extensions = 2
user_name = 'someUserName'
trainer_id = 'someTrainerId'
server_address = 'someServer'
device_name = 'someDeviceName'
user_badge_code = 'someBadgeCode'
trainer_badge_code = 'someTrainerBadgeCode'


class CustomAssertions(object):

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def assertTransitions(self, device, transitions=None, max_wait_time=5):
        transitions = transitions if transitions is not None and len(transitions) > 0 else []

        current = time.time()
        while transitions != device.transitions() and time.time() - current < max_wait_time:
            time.sleep(0.5)

        # This fixed wait of 5 seconds ensures that no other events have trigger additional unexpected transitions
        time.sleep(5)
        if transitions != device.transitions():
            raise AssertionError(
                'Actual transitions:\'{0}\' are not equal to expected transitions \'{1}\''
                .format(device.transitions(), transitions)
            )


class ClientDaemonTest(unittest.TestCase, CustomAssertions):

    def test_idle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            opts = get_default_opts(temp_dir)
            with VirtualDevice(opts) as device:
                self.assertTransitions(device, [
                    State.INITIALIZED,
                    State.IDLE
                ])

    def test_good_login(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            opts = get_default_opts(temp_dir)

            mock_response = Mock()
            mock_response.json.return_value = {
                'username': user_name,
                'devicename': device_name,
                'userid': user_id,
                'time': session_seconds,
                'remaining_extensions': remaining_extensions
            }

            with patch.object(requests, 'get', return_value=mock_response), VirtualDevice(opts) as device:
                device.scan_badge('some_badge_code')
                self.assertTransitions(device, [
                    State.INITIALIZED,
                    State.IDLE,
                    State.IN_USE
                ])

                # TODO: assertDisplay (current display message)
                # TODO: assertPins (current pin state from GPIO)

    def test_bad_login(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            opts = get_default_opts(temp_dir)
            mock_response = Mock()
            mock_response.json.return_value = {
                'username': user_name,
                'devicename': device_name,
                'userid': user_id,
                'time': 0,
                'remaining_extensions': remaining_extensions
            }

            with patch.object(requests, 'get', return_value=mock_response), VirtualDevice(opts) as device:
                device.scan_badge('some_badge_code')
                self.assertTransitions(device, [
                    State.INITIALIZED,
                    State.IDLE
                ])

                # TODO: assertDisplay (current display message)
                # TODO: assertPins (current pin state from GPIO)
