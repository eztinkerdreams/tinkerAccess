import os
import sys
import time
import logging
from subprocess import \
    call, \
    check_output, \
    CalledProcessError

from Client import Client
from Command import Command
from ClientSocket import ClientSocket
from daemonize import Daemonize
from PackageInfo import PackageInfo
from ClientOption import ClientOption


# noinspection PyClassHasNoInit
class ClientDaemon:

    @staticmethod
    def start(opts, args):
        logger = logging.getLogger(__name__)
        if not ClientDaemon.__status(opts, args):
            try:
                client = Client()
                pid_file = opts.get(ClientOption.PID_FILE)
                foreground = opts.get(ClientOption.DEBUG)
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
    def stop(opts, args):
        logger = logging.getLogger(__name__)
        pid_file = opts.get(ClientOption.PID_FILE)
        logout_coast_time = opts.get(ClientOption.LOGOUT_COAST_TIME)
        try:
            # Wait for what we assume will be a graceful exit
            ClientDaemon.__stop(opts, args)
            remaining_logout_coast_time = logout_coast_time
            while remaining_logout_coast_time and os.path.isfile(pid_file):
                remaining_logout_coast_time -= 1
                time.sleep(1)

            # if any processes still exists at this point... we will become more persuasive...
            for pid in check_output(['pgrep', '-f', '{0} start'.format(
                    PackageInfo.pip_package_name)]).splitlines():
                try:
                    call(['kill', '-9', pid])
                except Exception as e:
                    logger.exception(e)
        except CalledProcessError:
            pass

        # if the pid file still exist at this point... nuke it from orbit!
        if os.path.isfile(pid_file):
            try:
                os.remove(pid_file)
            except Exception as e:
                logger.exception(e)

    @staticmethod
    def restart(opts, args):
        logger = logging.getLogger(__name__)
        try:
            args[0] = Command.STOP.get('command')
            ClientDaemon.stop(opts, args)
            args[0] = Command.START.get('command')
            ClientDaemon.start(opts, args)
        except Exception as e:
            logger.debug('%s restart failed.', PackageInfo.pip_package_name)
            logger.exception(e)
            raise e

    # @staticmethod
    # def update(opts, args):
    #     pass

    # noinspection PyUnusedLocal
    @staticmethod
    def status(opts, args):
        logger = logging.getLogger(__name__)
        status = ClientDaemon.__status(opts, args)
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
    def __status(opts, args):
        # noinspection PyBroadException
        try:
            with ClientSocket() as socket:
                return socket.send(opts, args)
        except Exception:
            pass

    @staticmethod
    def __stop(opts, args):
        # noinspection PyBroadException
        try:
            with ClientSocket() as socket:
                socket.send(opts, args)
        except Exception:
            pass

