from setuptools import setup, find_packages
from setuptools.command.install import install as _install

from tinker_access_client.ServiceInstaller import ServiceInstaller
from tinker_access_client.PackageInfo import PackageInfo


# noinspection PyClassHasNoInit,PyPep8Naming
class install(_install):
    def run(self):
        _install.run(self)
        msg = "\nInstalling {0} service...".format(PackageInfo.python_package_name)

        # TODO: maybe change this to just use subprocess call in a loop['tinker-access-client install-service', etc..]
        self.execute(ServiceInstaller.install, (self.install_lib,), msg=msg)


config = {
    'name': PackageInfo.pip_package_name,
    'description': PackageInfo.pip_package_name,
    'author': 'Erick McQueen',
    'url': 'http://github.com/tinkerMill/tinkerAccess',
    'download_url': 'https://github.com/tinkerAccess/archive/v{0}.tar.gz'.format(PackageInfo.version),
    'author_email': 'ronn.mcqueen@tinkermill.org',
    'version': PackageInfo.version,
    'zip_safe': False,
    'include_package_data': True,
    'package_data': {
        PackageInfo.python_package_name: [
            'scripts/*'
        ]
    },
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
        'daemonize==2.4.7',
        'pyserial==3.2.1',
        'requests==2.12.4',
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
