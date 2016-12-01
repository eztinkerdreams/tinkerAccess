import os
import sys
import signal
import time
import logging
from subprocess import \
    check_output, \
    CalledProcessError

from Client import Client
from Command import Command
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
        logout_coast_time = opts.get(ClientOption.LOGOUT_COAST_TIME)
        max_power_down_timeout = opts.get(ClientOption.MAX_POWER_DOWN_TIMEOUT)

        try:
            for pid in check_output(['pgrep', '-f', '(/{0}\s+(start|restart))'.format(PackageInfo.pip_package_name)]).splitlines():
                is_current_pid = int(pid) == int(os.getpid())
                if not is_current_pid:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                    except Exception as e:
                        logger.exception(e)
        except CalledProcessError:
            pass

        # Wait for what we assume will be a graceful exit,
        # this will exit early if the pid file is removed as expected.
        current = time.time()
        max_wait_time = max_power_down_timeout + logout_coast_time + 5
        while time.time() - current < max_wait_time and os.path.isfile(pid_file):
            time.sleep(0.1)

        # This should never happen, but... if the pid file still exist at this point, we will nuke it from orbit!
        # Otherwise it will prevent the client daemon from starting again...
        if os.path.isfile(pid_file):
            try:
                os.remove(pid_file)
            except Exception as e:
                logger.exception(e)

    @staticmethod
    def restart(opts, args):
        logger = logging.getLogger(__name__)
        restart_delay = opts.get(ClientOption.RESTART_DELAY)
        try:
            args[0] = Command.STOP.get('command')
            ClientDaemon.stop(opts, args)
            logger.debug('Restarting in %s seconds...', restart_delay)
            time.sleep(restart_delay)
            args[0] = Command.START.get('command')
            ClientDaemon.start(opts, args)
        except Exception as e:
            logger.debug('%s restart failed.', PackageInfo.pip_package_name)
            logger.exception(e)
            raise e

    @staticmethod
    def status(opts, args):
        status = ClientDaemon.__status(opts, args)
        if status:
            sys.stdout.write(status)
            sys.stdout.flush()
            sys.exit(0)
        else:
            sys.exit(1)

    @staticmethod
    def __status(opts, _):
        status_file = opts.get(ClientOption.STATUS_FILE)

        status = terminated = 'terminated'
        if os.path.isfile(status_file):
            with open(status_file, 'r') as f:
                status = f.readline()

        return status if status is not terminated else None

