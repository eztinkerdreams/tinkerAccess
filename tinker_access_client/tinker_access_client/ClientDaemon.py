import os
import sys
import time


# TODO: convert to use LoggedPopen utility...
from subprocess import call, CalledProcessError, check_output

from Client import Client
from Command import Command
from ClientSocket import ClientSocket
from daemonize import Daemonize
from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
from ClientOption import ClientOption
from ClientOptionParser import ClientOptionParser


# noinspection PyClassHasNoInit


class ClientDaemon:

    @staticmethod
    def start():
        logger = ClientLogger.setup()
        opts = ClientOptionParser().parse_args()[0]
        pid_file = opts.get(ClientOption.PID_FILE)
        foreground = opts.get(ClientOption.DEBUG)

        if not ClientDaemon.__status():
            logger.debug('Attempting to start %s...', PackageInfo.pip_package_name)
            try:
                client = Client()
                daemon = Daemonize(
                    app=PackageInfo.pip_package_name,
                    pid=pid_file,
                    action=client.run,
                    foreground=foreground,
                    verbose=True,
                    logger=logger,
                    auto_close_fds=False
                )
                daemon.start()
            except Exception as e:
                logger.debug('%s start failed.', PackageInfo.pip_package_name)
                logger.exception(e)
                raise e
        else:
            sys.stdout.write('{0} is already running...\n'.format(PackageInfo.pip_package_name))
            sys.stdout.flush()
            sys.exit(1)

    @staticmethod
    def stop():
        logger = ClientLogger.setup()
        opts = ClientOptionParser().parse_args()[0]

        # Attempt to gracefully shutdown...
        logger.debug('Attempting to stop %s...', PackageInfo.pip_package_name)
        if ClientDaemon.__status():
            ClientDaemon.__stop()

        # if any processes still exists at this point... we will become more persuasive...
        try:
            for pid in check_output(['pgrep', '-f', '{0} start'.format(PackageInfo.pip_package_name)]).splitlines():
                try:
                    logger.debug('Attempting to kill pid: %s', pid)
                    call(['kill', '-9', pid])
                except Exception as e:
                    logger.exception(e)
        except CalledProcessError:
            pass

        # if the pid file still exist, nuke it from orbit
        pid_file = opts.get(ClientOption.PID_FILE)
        if os.path.isfile(pid_file):
            try:
                logger.debug('Attempting to delete pid_file %s', pid_file)
                os.remove(pid_file)
            except Exception as e:
                logger.exception(e)
                raise e

    @staticmethod
    def restart():
        # TODO: restart should wait until the client is idle.. not in use...

        logger = ClientLogger.setup()
        logger.debug('Attempting to restart %s...', PackageInfo.pip_package_name)
        try:
            ClientDaemon.stop()
            ClientDaemon.start()

        except Exception as e:
            logger.debug('%s restart failed.', PackageInfo.pip_package_name)
            logger.exception(e)
            raise e

    @staticmethod
    def status():
        logger = ClientLogger.setup()
        logger.debug('Attempting to check %s status...', PackageInfo.pip_package_name)

        status = ClientDaemon.__status()
        if status:
            sys.stdout.write('Status: {0}\n'.format(status))
            sys.stdout.flush()
            sys.exit(0)

        sys.stdout.write('the {0} is unavailable...\n'
                         'It may need to be restarted, try: \'sudo {0} restart\'\n'
                         .format(PackageInfo.pip_package_name))
        sys.stdout.flush()
        sys.exit(1)

    @staticmethod
    def __status():
        # noinspection PyBroadException
        try:
            with ClientSocket() as socket:
                return socket.send(Command.STATUS)

        except Exception:
            pass

        return None

    @staticmethod
    def __stop():
        opts = ClientOptionParser().parse_args()[0]
        logout_coast_time = opts.get(ClientOption.LOGOUT_COAST_TIME)

        # noinspection PyBroadException
        try:
            with ClientSocket(logout_coast_time) as socket:
                socket.send(Command.STOP)
                time.sleep(logout_coast_time)  # TODO: look for ways to exit early here...

        except Exception:
            pass

        return None

