from __future__ import absolute_import

import os
import time
import tempfile
import unittest
import requests
from mock import patch, Mock
from backports import tempfile

from tinker_access_client.tinker_access_client.State import State
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


# noinspection PyPep8Naming,PyMethodMayBeStatic
class CustomAssertions(object):

    def assertIdlePins(self, opts, device):
        self.assertPins(device, [
            (opts.get(ClientOption.PIN_POWER_RELAY), False),
            (opts.get(ClientOption.PIN_LED_RED), False),
            (opts.get(ClientOption.PIN_LED_GREEN), False),
            (opts.get(ClientOption.PIN_LED_BLUE), True),
        ])

    def assertInUsePins(self, opts, device):
        self.assertPins(device, [
            (opts.get(ClientOption.PIN_POWER_RELAY), True),
            (opts.get(ClientOption.PIN_LED_RED), False),
            (opts.get(ClientOption.PIN_LED_GREEN), True),
            (opts.get(ClientOption.PIN_LED_BLUE), False),
        ])

    def assertPins(self, device, pins=None):
        pins = pins if pins is not None else []

        for (pin, expected_pin_value) in pins:
            actual_pin_value = device.read_pin(pin)
            if expected_pin_value != actual_pin_value:
                raise AssertionError(
                    'Actual pin value:\'{0}\' are not equal to expected pin value \'{1}\''
                    .format(actual_pin_value, expected_pin_value)
                )

    def assertTransitions(self, device, transitions=None, max_wait_time=5):
        transitions = transitions if transitions is not None else []

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


class ClientTest(unittest.TestCase, CustomAssertions):

    def test_idle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            opts = get_default_opts(temp_dir)
            with VirtualDevice(opts) as device:

                self.assertTransitions(device, [
                    State.INITIALIZED,
                    State.IDLE
                ])

                self.assertIdlePins(opts, device)

    def test_good_login(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            opts = get_default_opts(temp_dir)

            valid_login_response = Mock()
            valid_login_response.json.return_value = {
                'username': user_name,
                'devicename': device_name,
                'userid': user_id,
                'time': session_seconds,
                'remaining_extensions': remaining_extensions
            }

            with patch.object(requests, 'get', return_value=valid_login_response), VirtualDevice(opts) as device:
                device.scan_badge('some_badge_code')

                self.assertTransitions(device, [
                    State.INITIALIZED,
                    State.IDLE,
                    State.IN_USE
                ])

                self.assertInUsePins(opts, device)

    def test_bad_login(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            opts = get_default_opts(temp_dir)
            invalid_login_response = Mock()
            invalid_login_response.json.return_value = {
                'username': user_name,
                'devicename': device_name,
                'userid': user_id,
                'time': 0,
                'remaining_extensions': remaining_extensions
            }

            with patch.object(requests, 'get', return_value=invalid_login_response), VirtualDevice(opts) as device:
                device.scan_badge('some_badge_code')

                self.assertTransitions(device, [
                    State.INITIALIZED,
                    State.IDLE
                ])

                self.assertIdlePins(opts, device)
