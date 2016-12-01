import unittest

from tinker_access_client.tinker_access_client.PackageInfo import PackageInfo
from tinker_access_client.tinker_access_client.ClientOption import ClientOption
from tinker_access_client.tinker_access_client.ContextFilter import ContextFilter

device_id = 'some_device'
user_id = 'some_user_id'
user_name = 'some_user_name'
badge_code = 'some_badge_code'
device_name = 'some_device_name'


class TestContextFilter(unittest.TestCase):
    def setUp(self):

        context_filter = ContextFilter({
            ClientOption.DEVICE_ID: device_id
        })

        context_filter.update_user_context({
            'user_id': user_id,
            'user_name': user_name,
            'badge_code': badge_code,
            'device_name': device_name
        })

        context_filter.filter(record=self)

    def test_filter(self):
        self.assertTrue(self.user_id == user_id)
        self.assertTrue(self.user_name == user_name)
        self.assertTrue(self.device_id == device_id)
        self.assertTrue(self.badge_code == badge_code)
        self.assertTrue(self.device_name == device_name)
        self.assertTrue(self.version == PackageInfo.version)
        self.assertTrue(self.app_id == PackageInfo.pip_package_name)
