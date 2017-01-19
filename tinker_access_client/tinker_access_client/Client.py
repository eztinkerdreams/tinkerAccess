import sys
import time

import errno
import socket
from socket import error as socket_error

# from threading import Thread
import thread

from transitions import Machine
# TODO: Enable LockedHierarchicalGraphMachine https://github.com/tyarkoni/transitions#-extensions
# from transitions.extensions import LockedHierarchicalGraphMachine as Machine

from Command import Command
from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
from DeviceApi import DeviceApi, Channel
from RemoteCommandHandler import RemoteCommandHandler
from ClientOptionParser import ClientOptionParser, ClientOption


class State(object):
    INITIALIZED = 'INITIALIZED'
    IDLE = 'IDLE'


class Client(Machine):
    def __init__(self):
        self.__logger = ClientLogger.setup()
        self.__opts = ClientOptionParser().parse_args()[0]
        self.__should_exit = False

        states = []
        for key, _ in vars(State).items():
            if not key.startswith('__'):
                states.append(key)

        Machine.__init__(self, states=states, initial=State.INITIALIZED)

    #This will be moved to some other class I am sure...
    def run_listener(self):
        self.__logger.debug('Attempting to establish %s listener...', PackageInfo.pip_package_name)

        server = None

        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            #TODO: this line causes some major proble, no exception is thrown
            #listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            server.bind(('', 8089))
            server.settimeout(None)
            server.listen(5)

            now = time.time()
            while not self.__should_exit:
                self.__logger.debug('listener started...')
                client = None

                try:
                    (client, addr) = server.accept()
                    command = Command(client.recv(1024))
                    if command:
                        self.__logger.debug('%s listener received \'%s\' command',
                                            PackageInfo.pip_package_name, command)

                        #TODO: allow for graceful shutdown..
                        if command is Command.STOP:
                            self.__stop()
                            break
                        else:
                            # send a standard response, possibly JSON...
                            client.send('State: {0}'.format(self.state))

                    client.shutdown(socket.SHUT_RDWR)

                except socket_error as e:
                    if e.errno != errno.ENOTCONN:
                        self.__logger.exception(e)
                        raise e

                except Exception as e:
                    self.__logger.exception(e)
                    raise e

                finally:
                    if client:
                        client.close()

                if not self.__should_exit:
                    self.__logger.debug('will stop listening...')

        except Exception as e:
            self.__logger.debug('Unable to establish the %s listener.', PackageInfo.pip_package_name)
            self.__logger.exception(e)
            thread.interrupt_main()

        finally:
            if server:
                server.shutdown(socket.SHUT_RDWR)
                server.close()

    def __handle_status_command(self, **kwargs):
        pass

    def __handle_stop_command(self, **kwargs):
        self.__stop()

    def __stop(self):
        self.__should_exit = True
        #TODO: wait for client status(self.state) to be done before we exit...

    def __do_something(self):
        self.__logger.debug('do something...')

    def __trigger_logout(self):
        self.__logger.debug('trigger logout..')

    def __trigger_training_mode(self):
        self.__logger.debug('trigger training..')

    def __trigger_login(self):
        self.__logger.debug('trigger training..')

    def __run(self):
        opts = self.__opts

        with RemoteCommandHandler() as handler, DeviceApi(opts) as device:
            handler.on(Command.STOP, self.__handle_stop_command)
            handler.on(Command.STATUS, self.__handle_status_command)

            device.on(
                Channel.SERIAL,
                direction=device.GPIO.IN,
                call_back=self.__trigger_login
            )

            device.on(
                Channel.PIN,
                pin=opts.get(ClientOption.PIN_LOGOUT),
                direction=device.GPIO.RISING,
                call_back=self.__trigger_logout
            )

            #TODO: not sure if this will actually work as expected, if we will get two calls, or they will conflict
            device.on(
                Channel.PIN,
                pin=opts.get(ClientOption.PIN_LOGOUT),
                direction=device.GPIO.RISING,
                call_back=self.__trigger_training_mode,
                debounce_delay=2000
            )

            while not self.__should_exit:
                self.__logger.debug('%s is waiting...', PackageInfo.pip_package_name)
                device.wait()

    def run(self):
        while not self.__should_exit:
            try:
                self.__logger.debug('Attempting to start the %s...', PackageInfo.pip_package_name)
                self.__run()
            except Exception as e:
                self.__logger.debug('%s failed.', PackageInfo.pip_package_name)
                self.__logger.exception(e)

            self.__logger.debug('Retrying in 5 seconds...')
            time.sleep(5)


