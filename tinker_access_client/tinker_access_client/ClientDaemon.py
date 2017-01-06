import os
import sys
import errno
import socket
from socket import error as socket_error


# TODO: convert to use LoggedPopen utility...
from subprocess import call, check_output

from Client import Client
from Command import Command
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

        # TODO: if there is an orphan pid.. than we will never start again,
        # need to add some code to destroy the pid if it already exists
        # or throw a meaningful exception
        # need to add test around starting the client twice, or use semephore pattern etc...

        if not os.path.isfile(pid_file):
            logger.debug('Attempting to start the %s daemon...', PackageInfo.pip_package_name)
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
                logger.debug('%s daemon start failed.', PackageInfo.pip_package_name)
                logger.exception(e)
                raise e
        else:
            raise RuntimeError('pid already exists...')   # TODO better message needed

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
            ClientDaemon.stop()
            ClientDaemon.start()

        except Exception as e:
            logger.debug('%s daemon restart failed.', PackageInfo.pip_package_name)
            logger.exception(e)
            raise e

    @staticmethod
    def status():
        logger = ClientLogger.setup()
        (opts, args) = ClientOptionParser().parse_args()

        ################################################################################################################
        # TODO: refactor to common util to send/receive message from client process
        ################################################################################################################
        client_socket = None
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #client_socket.settimeout(2)
            client_socket.settimeout(5)
            logger.debug('connecting...: %s', client_socket.getsockname())
            client_socket.connect(('', 8089))
            logger.debug('connected....')
            logger.debug('sending.......: %s', args[0])
            x = client_socket.send(args[0])
            logger.debug('sent.......: %s', x)

            logger.debug('recv.......')
            data = client_socket.recv(1024)
            logger.debug('data.......')
            ## TODO: this blocks...  which means it will cause issues with the service implementation
            ## we will need to do thread start, thread. join I think...?
            ## status command should return the current state of the machine...
            logger.debug('received: %s', data)
            client_socket.shutdown(socket.SHUT_RDWR)

        except socket_error as e:
            if e.errno != errno.ENOTCONN:
                logger.exception(e)
                raise e

        except Exception as e:
            logger.exception(e)
            raise e

        finally:
            if client_socket:
                client_socket.close()
        ################################################################################################################

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
