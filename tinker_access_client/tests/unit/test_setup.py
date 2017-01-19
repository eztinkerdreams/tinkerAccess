import unittest
from mock import patch

import setuptools

from tinker_access_client.tinker_access_client.PackageInfo import PackageInfo


@unittest.skip("temporarily disabled")
class TestSetup(unittest.TestCase):

    @patch.object(setuptools, 'setup')
    def test_setup(self, mock_setup):
        PackageInfo.version = 'v1.0-testing'
        # noinspection PyUnresolvedReferences
        import tinker_access_client.setup
        self.assertEqual(mock_setup.call_count, 1)
        self.assertEqual(mock_setup.call_args[1]['version'], 'v1.0-testing')

