from os import chmod
from subprocess import Popen, PIPE
from PackageInfo import PackageInfo
from ClientLogger import ClientLogger


class ServiceInstaller(object):

    @staticmethod
    def install(install_lib):
        logger = ClientLogger.setup(phase='install')
        logger.debug('Attempting to install the %s service...', PackageInfo.pip_package_name)
        try:
            install_script = '{0}{1}/scripts/install.sh'.format(install_lib, PackageInfo.python_package_name)
            service_script = '{0}{1}/Service.py'.format(install_lib, PackageInfo.python_package_name)
            chmod(install_script, 0755)
            chmod(service_script, 0755)
            cmd = [install_script, '-evx']
            install_process = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout_data, stderr_data = install_process.communicate()
            if install_process.returncode != 0:
                for ln in stderr_data.splitlines(True):
                    logger.error(ln)
                raise RuntimeError('%s service installation failed.' % PackageInfo.pip_package_name)
            else:
                for ln in stdout_data.splitlines(True):
                    logger.debug(ln)
        except Exception as e:
            logger.exception(e)
            raise e

        logger.debug('the %s service installation succeeded.', PackageInfo.pip_package_name)

