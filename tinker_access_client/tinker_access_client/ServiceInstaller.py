import os
import time
import tempfile
import subprocess

from PackageInfo import PackageInfo
from ClientLogger import ClientLogger


class ServiceInstaller(object):
    def __init__(self, install_lib):
        self.__logger = ClientLogger.setup(phase='install')

        self.__install_lib = install_lib
        self.__service_link = "/etc/init.d/{0}".format(PackageInfo.pip_package_name)
        self.__service_script = '{0}{1}/Service.py'.format(install_lib, PackageInfo.python_package_name)

    def install(self):
        try:
            self.__remove_legacy_client()  # TODO: remove after upgrade
            self.__create_service()
            self.__configure_service()

            # TODO: configure/enable auto-updates?

        except Exception as e:
            self.__logger.debug('%s service installation failed.', PackageInfo.pip_package_name)
            self.__logger.exception(e)
            raise e

    # noinspection PyMethodMayBeStatic
    def __ensure_execute_permission(self, path):
        os.chmod(path, 0755)

    # TODO: this can be removed after the upgrade
    def __remove_legacy_client(self):
        self.__execute_commands([
            'service tinkerclient stop\n',
            'update-rc.d -f tinkerclient remove\n',
            'rm -rf /etc/init.d/tinkerclient\n',
            'rm -rf /opt/tinkeraccess/client.py\n',
            'rm -rf /opt/tinkeraccess/client.pyc\n',
            'rm -rf /opt/tinkeraccess/lcdModule.py\n',
            'rm -rf /opt/tinkeraccess/lcdModule.pyc\n',
            'rm -rf /opt/tinkeraccess/client.cfg\n'
        ])

    def __create_service(self):
        self.__ensure_execute_permission(self.__service_script)

        # remove any existing service if it is a file or directory, and it is not a symlink
        if os.path.exists(self.__service_link) and not os.path.islink(self.__service_link):
            os.remove(self.__service_link)

        # remove the existing service if it is a symlink and it is not pointed to the current target
        if os.path.lexists(self.__service_link) and os.readlink(self.__service_link) != self.__service_script:
            os.remove(self.__service_link)

        # create the symlink if it doesn't already exists
        if not os.path.lexists(self.__service_link):
            os.symlink(self.__service_script, self.__service_link)

    def __configure_service(self):
        self.__execute_commands([
            # 'service {0} restart\n'.format(PackageInfo.pip_package_name)
            # # ,
            # # 'sleep 5\n',
            'update-rc.d {0} defaults 91\n'.format(PackageInfo.pip_package_name),
        ])

        # try:
        #     time.sleep(5)
        #     self.__execute_command('{0} restart'.format(PackageInfo.pip_package_name))
        #     # time.sleep(5)
        #     # self.__execute_command('service {0} start'.format(PackageInfo.pip_package_name))
        #     # # cmd = 'service {0} restart\n'.format(PackageInfo.pip_package_name)
        #     # self.__execute_commands([cmd])
        # except Exception as e:
        #     self.__logger.debug('command failed')
        #     self.__logger.exception(e)

    def __execute_commands(self, commands):

        # I suppose an explanation is warranted here...
        # Unfortunately we cannot execute these commands directly from python due to the fact that the
        # start priority 91 must be passed to the update-rc command as an integer and python converts all arguments to
        # strings which causes and exception when the update command is invoked.
        # We work around the problem by creating a temporary script file and executing that
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'w') as tmp:
                tmp.writelines(['#!/usr/bin/env bash \n'] + commands)
            self.__ensure_execute_permission(path)
            self.__execute_command(path)
        finally:
            os.remove(path)

    def __execute_command(self, command):
        cmd = [command] + ['-evx']  # Options: http://www.tldp.org/LDP/abs/html/options.html
        self.__logger.debug('Attempting to execute: %s', cmd)
        cmd_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data, stderr_data = cmd_process.communicate()
        if cmd_process.returncode != 0:
            for ln in stderr_data.splitlines(True):
                self.__logger.error(ln)
            raise RuntimeError('{0} command failed.'.format(cmd))


