import time
import threading

from transitions import Machine
# TODO: Enable LockedHierarchicalGraphMachine https://github.com/tyarkoni/transitions#-extensions
# from transitions.extensions import LockedHierarchicalGraphMachine as Machine

from Command import Command
from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
from DeviceApi import DeviceApi, Channel
from RemoteCommandHandler import RemoteCommandHandler
from ClientOptionParser import ClientOptionParser, ClientOption

logout_timer_interval_seconds = 1


class State(object):
    IDLE = 'IDLE'
    IN_USE = 'IN_USE'
    INITIALIZED = 'INITIALIZED'
    IN_FAULT = 'IN_FAULT'


class Trigger(object):
    IDLE = 'idle'
    LOGIN = 'login'
    LOGOUT = 'logout'


class Client(Machine):
    def __init__(self):
        self.__device = None
        self.__user_info = None
        self.__logout_timer = None
        self.__should_exit = False
        self.__logger = ClientLogger.setup()
        self.__opts = ClientOptionParser().parse_args()[0]

        states = []
        for key, _ in vars(State).items():
            if not key.startswith('__'):
                states.append(key)

        transitions = [
            {
                'trigger': Trigger.IDLE,
                'source': State.INITIALIZED,
                'dest': State.IDLE
            },
            {
                'trigger': Trigger.LOGIN,
                'source': State.IDLE,
                'dest': State.IN_USE,
                'conditions': 'authorized'
            },

            # TODO: handle case where use re-badges in, or another users badges in while the machine is in use
            # {
            #     'trigger': Trigger.LOGIN,
            #     'source': State.IN_USE,
            #     'dest': State.IN_USE,
            #     'conditions': 're-authorized' #extend time if same user, otherwise go through login process
            # },

            {
                'trigger': Trigger.LOGIN,
                'source': State.IDLE,
                'dest': State.IDLE,
                'unless': 'authorized',
                'before': 'not_authorized'
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

        # what if device is in use, should stop return error, or forcefully do a stop?
        # TODO: wait for client status(self.state) to be done before we exit...
        # i.e. logout should be complete etc...

        self.__should_exit = True
        self.logout()

    def __handle_status_command(self, **kwargs):
        return self.state

    def __enable_power(self):
        self.__device.write(Channel.PIN, self.__opts.get(ClientOption.PIN_POWER_RELAY), True)

    def __disable_power(self):
        self.__device.write(Channel.PIN, self.__opts.get(ClientOption.PIN_POWER_RELAY), False)

    def __do_logout(self):
        self.__cancel_logout_timer()

        if self.__user_info:
            pass
            # ServerApi.doLogout

        self.__user_info = None

    def __ensure_idle(self):
        self.__do_logout()
        self.__disable_power()
        self.__device.write(Channel.LED, False, False, True)

    def __ensure_in_use(self):
        self.__enable_power()
        self.__device.write(Channel.LED, False, True, False)

    def __logout_timer_tick(self, remaining_seconds):
        remaining_seconds -= logout_timer_interval_seconds

        if remaining_seconds <= 0:
            self.logout()
            return

        if remaining_seconds < 300:
            self.__device.write(Channel.LED, True, False, False)

        self.__device.write(Channel.LCD, 'Access granted', 'Time Remaining: {0}s'.format(remaining_seconds))

        self.__logout_timer = threading.Timer(
            logout_timer_interval_seconds,
            self.__logout_timer_tick,
            [remaining_seconds, ]
        )
        self.__logout_timer.start()

    def __cancel_logout_timer(self):
        if self.__logout_timer:
            self.__logout_timer.cancel()

    def __start_logout_timer(self, remaining_seconds):
        self.__cancel_logout_timer()
        self.__logout_timer = threading.Timer(
            logout_timer_interval_seconds,
            self.__logout_timer_tick,
            [remaining_seconds, ]
        )
        self.__logout_timer.start()

    def authorized(self, *args, **kwargs):
        if not self.__user_info:
            badge_code = kwargs.get('badge_code')
            if badge_code:

                # ServerApi.doLogin
                if badge_code == 'bar':
                    self.__user_info = badge_code

        return self.__user_info is not None

    def not_authorized(self, *args, **kwargs):
        self.__device.write(Channel.LED, True, False, False)
        self.__device.write(Channel.LCD, 'Access Denied', 'Take the class')
        time.sleep(2)

    # noinspection PyPep8Naming
    def on_enter_IN_FAULT(self):
        self.__device.fault()

    # noinspection PyPep8Naming
    def on_enter_IN_USE(self, *args, **kwargs):
        self.__ensure_in_use()
        self.__device.write(Channel.LCD, 'Access granted')

        # TODO: include user_name, time_remaining, in Access granted for % s granted with time % s"
        # TODO: start timer for logout trigger

        remaining_seconds = 60  # use value returned from service call, total remaining time should be in seconds
        self.__start_logout_timer(remaining_seconds)

    # noinspection PyPep8Naming
    def on_enter_IDLE(self, *args, **kwargs):
        self.__ensure_idle()
        self.__device.write(Channel.LCD, 'Scan Badge', 'To Login')

    def __run(self):
        opts = self.__opts

        with RemoteCommandHandler() as handler, DeviceApi(opts) as device:
            self.__device = device

            handler.on(Command.STOP, self.__handle_stop_command)
            handler.on(Command.STATUS, self.__handle_status_command)
            handler.listen()

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

            self.idle()
            while not self.__should_exit:
                self.__logger.debug('%s is waiting...', PackageInfo.pip_package_name)
                device.wait()

    def run(self):
        while not self.__should_exit:
            try:
                self.__run()
            except Exception as e:
                self.set_state(State.IN_FAULT)
                self.__logger.debug('%s failed.', PackageInfo.pip_package_name)
                self.__logger.exception(e)

            self.__logger.debug('Retrying in 5 seconds...')
            time.sleep(5)
            self.set_state(State.INITIALIZED)
