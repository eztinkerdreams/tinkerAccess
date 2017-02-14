import os
import sys
import signal
import time
from subprocess import \
    check_output, \
    CalledProcessError

from State import State
from Client import Client
from Command import Command
from daemonize import Daemonize
from PackageInfo import PackageInfo
from ClientOption import ClientOption
from ClientLogger import ClientLogger
from LoggedRequest import LoggedRequest
from CommandExecutor import CommandExecutor


# noinspection PyClassHasNoInit
class ClientDaemon:

    @staticmethod
    def start(opts, args):
        logger = ClientLogger.setup()
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
        logger = ClientLogger.setup()
        pid_file = opts.get(ClientOption.PID_FILE)
        logout_coast_time = opts.get(ClientOption.LOGOUT_COAST_TIME)
        max_power_down_timeout = opts.get(ClientOption.MAX_POWER_DOWN_TIMEOUT)

        try:
            for process_id in ClientDaemon.__get_process_ids():
                try:
                    os.kill(process_id, signal.SIGTERM)
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
    def update(opts, args):

        #TODO: should take a version number as an argument, do update to that version

        if not PackageInfo.version:
            sys.stdout.write('The \'update\' command is not supported when\n')
            sys.stdout.write('when the {0} is not versioned. (i.e. installed with the development -e option.\n'
                             .format(PackageInfo.pip_package_name))
            sys.stdout.flush()
            sys.exit(1)

        if not ClientDaemon.__is_in_use(opts, args):
            logger = ClientLogger.setup()
            try:
                response = LoggedRequest.get('https://pypi.python.org/pypi/tinker-access-client/json')
                response.raise_for_status()
                latest_version = response.json()['info']['version']

                #TODO: check if this release exists... int the releases section

                logger.debug('latest version: %s', latest_version)
                logger.debug('current version: %s', PackageInfo.version)
                logger.debug('version match? %s', PackageInfo.version == latest_version)
                if PackageInfo.version != latest_version:

                    ClientDaemon.stop(opts, args)
                    CommandExecutor().execute_commands([
                        'pip install --upgrade --force-reinstall --ignore-installed --no-cache-dir {0}'
                        .format(PackageInfo.pip_package_name)
                    ])

            except Exception as e:
                logger.debug('%s update failed, remediation maybe required!', PackageInfo.pip_package_name)
                logger.exception(e)
                raise e
        else:
            sys.stdout.write('{0} is currently in use, try again later...\n'.format(PackageInfo.pip_package_name))
            sys.stdout.flush()
            sys.exit(1)

    @staticmethod
    def restart(opts, args):
        logger = ClientLogger.setup()
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
            sys.stdout.write('{0}\n'.format(State.TERMINATED))
            sys.stdout.flush()
            sys.exit(1)

    @staticmethod
    def __status(opts, _):
        process_ids = ClientDaemon.__get_process_ids()
        status_file = opts.get(ClientOption.STATUS_FILE)

        status = terminated = State.TERMINATED
        if os.path.isfile(status_file):
            with open(status_file, 'r') as f:
                status = f.readline().strip()

        return status if status is not terminated and len(process_ids) > 0 else None

    @staticmethod
    def __is_in_use(opts, args):
        status = ClientDaemon.__status(opts, args)
        return status == State.IN_USE or status == State.IN_TRAINING

    @staticmethod
    def __get_process_ids():
        process_ids = []

        cmd = ['pgrep', '-f', '(/{0}\s+(start|restart|update))'.format(PackageInfo.pip_package_name)]
        for process_id in check_output(cmd).splitlines():
            process_id = int(process_id)
            is_current_process = process_id == int(os.getpid())
            if not is_current_process:
                process_ids.append(process_id)

        return process_ids
