from setuptools import setup, find_packages
from setuptools.command.install import install as _install

from tinker_access_client.ServiceInstaller import ServiceInstaller
from tinker_access_client.PackageInfo import PackageInfo


# noinspection PyClassHasNoInit,PyPep8Naming
class install(_install):
    def run(self):
        _install.run(self)
        msg = '\nInstalling {0} service...'.format(PackageInfo.python_package_name)
        self.execute(ServiceInstaller(self.install_lib).install, [], msg)


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
        'transitions',
        'daemonize',
        'pyserial',
        'requests',
        'retry'
    ],

    'packages': find_packages(exclude=('tests*',)),
    'test_suite': 'nose.collector',
    'tests_require': [
        'transitions',
        'daemonize',
        'pyserial',
        'requests',
        'mock',
        'nose'
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
