import os
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
            # TODO: legacy migration/removal

            self.__grant_execute_permission()
            self.__create_symbolic_link()
            self.__configure_service_to_start_on_boot()

            # TODO: configure/enable auto-updates?

        except Exception as e:
            self.__logger.debug('%s service installation failed.', PackageInfo.pip_package_name)
            self.__logger.exception(e)
            raise e

    def __grant_execute_permission(self):
        os.chmod(self.__service_script, 0755)

    def __create_symbolic_link(self):

        # remove any existing service if it is a file or directory, and it is not a symlink
        if os.path.exists(self.__service_link) and not os.path.islink(self.__service_link):
            os.remove(self.__service_link)

        # remove the existing service if it is a symlink and it is not pointed to the current target
        if os.path.lexists(self.__service_link) and os.readlink(self.__service_link) != self.__service_script:
            os.remove(self.__service_link)

        if not os.path.lexists(self.__service_link):
            os.symlink(self.__service_script, self.__service_link)

    def __configure_service_to_start_on_boot(self):
        self.__execute(['update-rc.d', PackageInfo.pip_package_name,  'defaults', '91'])

    def __restart_service(self):
        self.__execute(['service', PackageInfo.pip_package_name, 'restart'])

    def __execute(self, command):
        cmd = command + ['-evx']
        cmd_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data, stderr_data = cmd_process.communicate()
        if cmd_process.returncode != 0:
            for ln in stderr_data.splitlines(True):
                self.__logger.error(ln)
            raise RuntimeError('{0} command failed.'.format(cmd))

