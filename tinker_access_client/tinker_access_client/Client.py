import time
import errno
import socket
import thread
from socket import error as socket_error

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

    def __handle_stop_command(self, **kwargs):
        self.__stop()

    def __stop(self):

        #TODO: wait for client status(self.state) to be done before we exit...

        self.__should_exit = True

    def __handle_status_command(self, **kwargs):
        # TODO: return self.state...
        pass

    def __run(self):
        opts = self.__opts

        with RemoteCommandHandler() as handler, DeviceApi(opts) as device:
            handler.on(Command.STOP, self.__handle_stop_command)
            handler.on(Command.STATUS, self.__handle_status_command)

            def trigger_login():
                self.__logger.debug('trigger login..')

            def trigger_logout():
                if not device.read(Channel.PIN, opts.get(ClientOption.PIN_LOGOUT)):
                    self.__logger.debug('trigger logout..')
                else:
                    thread.Timer(2000, trigger_training_mode).start()

            def trigger_training_mode():
                # If the pin is still HIGH, then go into training mode a.k.a mario mode
                if device.read(Channel.PIN, opts.get(ClientOption.PIN_LOGOUT)):
                    self.__logger.debug('trigger training..')

            device.on(
                Channel.SERIAL,
                direction=device.GPIO.IN,
                call_back=trigger_login
            )

            device.on(
                Channel.PIN,
                pin=opts.get(ClientOption.PIN_LOGOUT),
                direction=device.GPIO.RISING,
                call_back=trigger_logout
            )

            # TODO: are there other things we can sense?
            # i.e. can we do automatic logout request if the machine is shutdown manually?

            while not self.__should_exit:
                self.__logger.debug('%s is waiting...', PackageInfo.pip_package_name)
                device.wait()

    def run(self):
        while not self.__should_exit:
            self.__logger.debug('Attempting to start the %s...', PackageInfo.pip_package_name)
            try:
                self.__run()
            except Exception as e:
                self.__logger.debug('%s failed.', PackageInfo.pip_package_name)
                self.__logger.exception(e)
            self.__logger.debug('Retrying in 5 seconds...')
            time.sleep(5)


