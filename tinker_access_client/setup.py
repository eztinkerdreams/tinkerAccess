import warnings
from setuptools import setup, find_packages
from setuptools.command.install import install as _install

from tinker_access_client.ServiceInstaller import ServiceInstaller
from tinker_access_client.PackageInfo import PackageInfo


# noinspection PyClassHasNoInit,PyPep8Naming,PyBroadException
class install(_install):
    def run(self):
        _install.run(self)
        msg = '\nInstalling the {0} service...'.format(PackageInfo.pip_package_name)

        try:
            self.execute(ServiceInstaller(self.install_lib).install, [], msg)
        except Exception:
            msg = 'The {0} service may not have installed correctly. \n' \
                  'Remediation maybe required!, Check syslog for more information.'.format(PackageInfo.pip_package_name)
            warnings.warn(msg)
            pass


config = {
    'name': PackageInfo.pip_package_name,
    'description': PackageInfo.pip_package_name,
    'author': 'Erick McQueen',
    'url': 'http://github.com/tinkerMill/tinkerAccess',
    'download_url': 'https://github.com/tinkerAccess/archive/v{0}.tar.gz'.format(PackageInfo.version),
    'author_email': 'ronn.mcqueen@tinkermill.org',
    'version': PackageInfo.version,
    'zip_safe': False,
    'install_requires': [
        'transitions==0.4.3',
        'daemonize==2.4.7',
        'requests==2.12.4',
        'pyserial==3.2.1',
        'retry==0.9.2'
    ],

    'packages': find_packages(exclude=('tests*',)),
    'test_suite': 'nose.collector',
    'tests_require': [
        'transitions==0.4.3',
        'daemonize==2.4.7',
        'requests==2.12.4',
        'pyserial==3.2.1',
        'mock==2.0.0',
        'nose==1.3.7'
    ],
    'entry_points': {
        'console_scripts': [
            '{0}={1}.Service:run'.format(PackageInfo.pip_package_name, PackageInfo.python_package_name)
        ]
    },
    'cmdclass': {
        'install': install
    }
}

setup(**config)
