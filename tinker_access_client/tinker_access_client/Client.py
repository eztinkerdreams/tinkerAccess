import time
import errno
import socket
import thread
import threading
from socket import error as socket_error

from pydash import debounce, delay, throttle
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
    IDLE = 'IDLE'
    IN_USE = 'IN_USE'
    INITIALIZED = 'INITIALIZED'
    IN_FAULT = 'IN_FAULT'


class Trigger(object):
    LOGIN = 'login'
    LOGOUT = 'logout'


class Client(Machine):
    def __init__(self):
        self.__device = None
        self.__should_exit = False
        self.__logger = ClientLogger.setup()
        self.__opts = ClientOptionParser().parse_args()[0]

        states = []
        for key, _ in vars(State).items():
            if not key.startswith('__'):
                states.append(key)

        transitions = [
            {
                'trigger': Trigger.LOGIN,
                'source': State.IDLE,
                'dest': State.IN_USE
            },
            {
                'trigger': Trigger.LOGOUT,
                'source': [State.IN_USE, State.IDLE],
                'dest': State.IDLE
            }
        ]

        Machine.__init__(self, states=states, transitions=transitions, initial=State.INITIALIZED)

    def __handle_stop_command(self, **kwargs):
        self.__stop()

    def __stop(self):

        # TODO: wait for client status(self.state) to be done before we exit...

        self.__should_exit = True

    def __handle_status_command(self, **kwargs):
        # TODO: work in progress... return self.state...
        pass

    def __enable_power(self):
        self.__device.write(Channel.PIN, self.__opts.get(ClientOption.PIN_POWER_RELAY), True)

    def __disable_power(self):
        self.__device.write(Channel.PIN, self.__opts.get(ClientOption.PIN_POWER_RELAY), False)

    def __do_logout(self):
        #ServerApi.doLogout
        pass

    def __ensure_idle(self):
        self.__do_logout()
        self.__disable_power()
        self.__device.write(Channel.LED, False, False, True)

    def __ensure_in_use(self):
        self.__enable_power()
        self.__device.write(Channel.LED, False, True, False)

    # noinspection PyPep8Naming
    def on_enter_IN_USE(self, *args, **kwargs):
        self.__ensure_in_use()
        #TODO: lcdOutput message

        self.__logger.debug('in_use')

    # noinspection PyPep8Naming
    def on_enter_IDLE(self, *args, **kwargs):
        self.__ensure_idle()
        #TODO: lcdOutput, scan badge message

        self.__logger.debug('idle')

    def __run(self, *args, **kwargs):
        self.__logger.debug('on_enter_IDLE: args: %s, kwargs: %s', args, kwargs)
        opts = self.__opts

        with RemoteCommandHandler() as handler, DeviceApi(opts) as device:
            self.__device = device
            handler.on(Command.STOP, self.__handle_stop_command)
            handler.on(Command.STATUS, self.__handle_status_command)

            device.on(
                Channel.SERIAL,
                direction=device.GPIO.IN,
                call_back=self.login
            )

            device.on(
                Channel.PIN,
                pin=opts.get(ClientOption.PIN_LOGOUT),
                direction=device.GPIO.RISING,
                call_back=self.logout
            )

            self.set_state(State.IDLE)
            while not self.__should_exit:
                self.__logger.debug('%s is waiting...', PackageInfo.pip_package_name)
                device.wait()

    def on_enter_IN_FAULT(self, *args, **kwargs):
        self.__device.fault()

    def run(self):
        while not self.__should_exit:
            self.__logger.debug('Attempting to start the %s...', PackageInfo.pip_package_name)
            try:
                self.__run()
            except Exception as e:
                self.set_state(State.IN_FAULT)
                #TODO: self.__device.remove_callbacks
                self.__logger.debug('%s failed.', PackageInfo.pip_package_name)
                self.__logger.exception(e)
            self.__logger.debug('Retrying in 5 seconds...')
            time.sleep(5)
            self.set_state(State.INITIALIZED)
