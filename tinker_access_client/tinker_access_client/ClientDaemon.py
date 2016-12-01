import os
import sys
import signal
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
                pid_file = opts.get(ClientOption.PID_FILE)
                foreground = opts.get(ClientOption.DEBUG)

                def start():
                    Client.run(opts, args)

                daemon = Daemonize(
                    app=PackageInfo.pip_package_name,
                    pid=pid_file,
                    action=start,
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
        try:
            for pid in check_output(['pgrep', '-f', '{0} start'.format(PackageInfo.pip_package_name)]).splitlines():
                try:
                    os.kill(int(pid), signal.SIGTERM)
                except Exception as e:
                    logger.exception(e)
        except CalledProcessError:
            pass

        # Wait for what we assume will be a graceful exit
        current = time.time()
        while os.path.isfile(pid_file) and time.time() - current < 5:
            time.sleep(0.1)

        #if the pid file still exist at this point... nuke it from orbit!
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
        status_file = opts.get(ClientOption.STATUS_FILE)

        status = terminated = 'terminated'
        if os.path.isfile(status_file):
            with open(status_file, 'r') as f:
                status = f.readline()

        sys.stdout.write(status)
        sys.stdout.flush()

        if status != terminated:
            sys.exit(0)
        else:
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

