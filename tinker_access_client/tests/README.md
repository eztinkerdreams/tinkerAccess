# Testing

To run tests, we can simply do:
```
    python setup.py test
```

The Setup tools will take care of installing dependencies (i.e. nose, mock) and running the test suite.

# TODO: add example to run a single test.
# TODO: add info about manual testing with --debug flag on non-rpi devices

```
% python setup.py test
running test
Searching for mock
Reading https://pypi.python.org/simple/mock/
Best match: mock 2.0.0
Downloading https://pypi.python.org/packages/0c/53/014354fc93c591ccc4abff12c473ad565a2eb24dcd82490fae33dbf2539f/mock-2.0.0.tar.gz#md5=0febfafd14330c9dcaa40de2d82d40ad
Processing mock-2.0.0.tar.gz
Writing /var/folders/02/1l6b42w97mjfk6mnyc8mx02wlr0dbg/T/easy_install-eA4ees/mock-2.0.0/setup.cfg
Running mock-2.0.0/setup.py -q bdist_egg --dist-dir /var/folders/02/1l6b42w97mjfk6mnyc8mx02wlr0dbg/T/easy_install-eA4ees/mock-2.0.0/egg-dist-tmp-wGr4hl
creating /Users/rmcqueen/projects/TinkerMill/tinkerAccess/tinker_access_client/.eggs/mock-2.0.0-py2.7.egg
Extracting mock-2.0.0-py2.7.egg to /Users/rmcqueen/projects/TinkerMill/tinkerAccess/tinker_access_client/.eggs

Installed /Users/rmcqueen/projects/TinkerMill/tinkerAccess/tinker_access_client/.eggs/mock-2.0.0-py2.7.egg
running egg_info
writing requirements to tinker_access_client.egg-info/requires.txt
writing tinker_access_client.egg-info/PKG-INFO
writing top-level names to tinker_access_client.egg-info/top_level.txt
writing dependency_links to tinker_access_client.egg-info/dependency_links.txt
reading manifest file 'tinker_access_client.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
writing manifest file 'tinker_access_client.egg-info/SOURCES.txt'
running build_ext
test_ClientOptionParser (tinker_access_client.tests.test_ClientConfigOptions.ClientOptionParserTests) ... ok
test_readPinReturnsTrueWhenInputMatchesExpectedState (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_readRaisesUnexpectedExceptions (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_readSerialRaisesUnexpectedExceptions (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_readSerialReturnsValue (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_setUpConfiguresDevice (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_setUpRaisesUnexpectedExceptions (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_writeLogsOutput (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_writeRaisesUnexpectedExceptions (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_writeToBlueLed (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_writeToGreenLed (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_writeToLcd (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_writeToPin (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_writeToRedLed (tinker_access_client.tests.test_DeviceApi.DeviceApiTests) ... ok
test_getLogsExceptions (tinker_access_client.tests.test_LoggedRequest.LoggedRequestTest) ... ok
test_getLogsRequest (tinker_access_client.tests.test_LoggedRequest.LoggedRequestTest) ... ok
test_getRaisesExceptionOnInValidResponse (tinker_access_client.tests.test_LoggedRequest.LoggedRequestTest) ... ok
test_loginRaisesUnauthorizedAccessException (tinker_access_client.tests.test_ServerApi.ServerApiTests) ... ok
test_loginRaisesUnexpectedExceptionFromRequests (tinker_access_client.tests.test_ServerApi.ServerApiTests) ... ok
test_loginReturnsLoginResponse (tinker_access_client.tests.test_ServerApi.ServerApiTests) ... ok
test_logoutCatchesUnexpectedExceptionFromRequests (tinker_access_client.tests.test_ServerApi.ServerApiTests) ... ok
test_registerUser (tinker_access_client.tests.test_ServerApi.ServerApiTests) ... ok
test_registerUserRaisesUnexpectedExceptionFromRequests (tinker_access_client.tests.test_ServerApi.ServerApiTests) ... ok
test_register_user_RaisesUserRegistrationException (tinker_access_client.tests.test_ServerApi.ServerApiTests) ... ok
test_foo (tinker_access_client.tests.test_tinker_access_client.RunTests) ... ok

----------------------------------------------------------------------
Ran 25 tests in 0.030s

```
