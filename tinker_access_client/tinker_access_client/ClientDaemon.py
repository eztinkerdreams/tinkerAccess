import os
import sys

# TODO: convert to use LoggedPopen utility...
from subprocess import call, check_output, CalledProcessError

from Client import Client
from daemonize import Daemonize
from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
from ClientOption import ClientOption
from ClientOptionParser import ClientOptionParser


# noinspection PyClassHasNoInit
class ClientDaemon:
    @staticmethod
    def start():
        # TODO: handle if process already running, can't lock on pid_file
        logger = ClientLogger.setup()
        opts = ClientOptionParser().parse_args()[0]
        pid_file = opts.get(ClientOption.PID_FILE)
        foreground = opts.get(ClientOption.DEBUG)
        logger.debug('Attempting to start the %s daemon...', PackageInfo.pip_package_name)
        try:
            client = Client()
            daemon = Daemonize(
                app=PackageInfo.pip_package_name, pid=pid_file,
                action=client.run,
                foreground=foreground, verbose=True,
                logger=logger
            )
            daemon.start()
        except Exception as e:
            logger.debug('%s daemon start failed.', PackageInfo.pip_package_name)
            logger.exception(e)
            raise e

    @staticmethod
    def stop():
        logger = ClientLogger.setup()
        opts = ClientOptionParser().parse_args()[0]
        pid_file = opts.get(ClientOption.PID_FILE)
        if os.path.isfile(pid_file): # TODO: maybe use while loop and timeout
            logger.debug('Attempting to stop the %s daemon...', PackageInfo.pip_package_name)
            try:
                # TODO: use call_output return, and set timeout, including logging etc..
                # should use a common util for when we need to kill a process like this

                # Also needs some work if the process is not already running
                call(['pkill', '-F', pid_file])
            except Exception as e:
                logger.debug('%s daemon stop failed.', PackageInfo.pip_package_name)
                logger.exception(e)
                raise e

    @staticmethod
    def restart():
        # TODO: restart should wait until the client is idle.. not in use...

        logger = ClientLogger.setup()
        logger.debug('Attempting to restart the %s daemon...', PackageInfo.pip_package_name)
        try:
            # TODO: this needs some work, the start method is creating duplicate threads

            # TODO: this try/catch blocks will be removed eventually
            try:
                ClientDaemon.stop()
            except Exception:
                pass

            ClientDaemon.start()

        except Exception as e:
            logger.debug('%s daemon restart failed.', PackageInfo.pip_package_name)
            logger.exception(e)
            raise e

    @staticmethod
    def status():
        logger = ClientLogger.setup()
        opts = ClientOptionParser().parse_args()[0]
        pid_file = opts.get(ClientOption.PID_FILE)
        logger.debug('Attempting to check the %s daemon status...', PackageInfo.pip_package_name)
        try:
            # TODO: use call_output return, and set timeout, including logging etc..
            # should use a common util for when we need to kill a process like this

            # Also needs some work if the process is not already running
            # TODO: can't seem to catch the exception here?
            FNULL = open(os.devnull, 'w')
            return_code = check_output(['pgrep', '-F', pid_file], stderr=FNULL)
            if return_code != 0:
                sys.stdout.write('running\n')
                sys.stdout.flush()
                return
        except Exception:
            pass
        # except CalledProcessError:
        #     pass
        # except Exception as e:
        #     pass
        #     # logger.debug('%s daemon status failed.', PackageInfo.pip_package_name)
        #     # logger.exception(e)
        #     # raise e
        sys.exit(1)
