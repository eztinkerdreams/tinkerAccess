import time
import logging
import threading
from transitions import Machine
# TODO: Enable LockedHierarchicalGraphMachine https://github.com/tyarkoni/transitions#-extensions
# from transitions.extensions import LockedHierarchicalGraphMachine as Machine

from Command import Command
from TinkerAccessServerApi import TinkerAccessServerApi
from PackageInfo import PackageInfo
from DeviceApi import DeviceApi, Channel
from RemoteCommandHandler import RemoteCommandHandler
from ClientOptionParser import ClientOptionParser, ClientOption
from UnauthorizedAccessException import UnauthorizedAccessException

maximum_lcd_characters = 16
training_mode_delay_seconds = 2
logout_timer_interval_seconds = 1


class State(object):
    IDLE = 'IDLE'
    IN_USE = 'IN_USE'
    IN_TRAINING = 'IN_TRAINING'
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
        self.__logger = logging.getLogger(__name__)
        self.__opts = ClientOptionParser().parse_args()[0]
        self.__tinkerAccessServerApi = TinkerAccessServerApi(self.__opts)

        states = []
        for key, _ in vars(State).items():
            if not key.startswith('__'):
                states.append(key)

        transitions = [
            {
                'source': State.INITIALIZED,
                'trigger': Trigger.IDLE,
                'dest': State.IDLE
            },

            {
                'source': State.IDLE,
                'trigger': Trigger.LOGIN,
                'dest': State.IN_USE,
                'conditions': ['is_authorized']
            },

            {
                'source': State.IN_USE,
                'trigger': Trigger.LOGIN,
                'dest': State.IN_USE,
                'conditions': ['is_current_badge_code']
            },

            {
                'source': [State.IN_USE, State.IDLE, State.IN_TRAINING],
                'trigger': Trigger.LOGOUT,
                'dest': State.IDLE,
                'unless': ['is_waiting_for_training']
            },

            {
                'source': [State.IDLE],
                'trigger': Trigger.LOGOUT,
                'dest': State.IN_TRAINING,
                'conditions': ['is_waiting_for_training']
            },

            {
                'source': [State.IN_TRAINING],
                'trigger': Trigger.LOGIN,
                'dest': State.IN_TRAINING
            }
        ]

        Machine.__init__(self, queued=True, states=states, transitions=transitions, initial=State.INITIALIZED)

    #
    # IDLE -- The machine is idle and waiting for a badge to be scanned
    #

    def __ensure_idle(self):
        self.__do_logout()
        self.__disable_power()
        self.__show_blue_led()
        self.__show_scan_badge()

    def __do_logout(self):
        self.__cancel_logout_timer()

        if self.__user_info:
            badge_code = self.__user_info.get('badge_code')
            # noinspection PyBroadException
            try:
                self.__tinkerAccessServerApi.logout(badge_code)
            except Exception:
                # ignore any exceptions, we don't care on logout,
                # other utilities further up the stack will log any exceptions
                pass

        self.__update_user_context(None)

    def __disable_power(self):
        self.__device.write(
            Channel.PIN, self.__opts.get(ClientOption.PIN_POWER_RELAY), False)

    def __show_blue_led(self):
        self.__device.write(Channel.LED, False, False, True)

    def __show_scan_badge(self):
        self.__device.write(
            Channel.LCD,
            'Scan Badge'.center(maximum_lcd_characters, ' '),
            'To Login'.center(maximum_lcd_characters, ' ')
        )

    #
    # IN_USE -- The machine is currently in use and the logout timer is ticking...
    #

    def __do_login(self, *args, **kwargs):
        badge_code = kwargs.get('badge_code')

        try:
            self.__show_attempting_login()
            self.__update_user_context(
                self.__tinkerAccessServerApi.login(badge_code)
            )
            remaining_seconds = self.__user_info.get('remaining_seconds')
            self.__logger.info('Access granted for %s with %s remaining_seconds', badge_code, remaining_seconds)
            self.__show_access_granted()
            time.sleep(1)

        except UnauthorizedAccessException:
            self.__show_access_denied()

        return self.__user_info is not None

    def __show_attempting_login(self):
        self.__device.write(
            Channel.LCD,
            'Attempting'.center(maximum_lcd_characters, ' '),
            'Login...'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(1)

    def __update_user_context(self, user_info):
        self.__user_info = user_info
        for context_filter in self.__logger.filters:
            update_user_context = getattr(context_filter, "update_user_context", None)
            if callable(update_user_context):
                context_filter.update_user_context(self.__user_info)

    def __ensure_in_use(self):
        self.__enable_power()
        self.__show_green_led()

    def __enable_power(self):
        self.__device.write(Channel.PIN, self.__opts.get(ClientOption.PIN_POWER_RELAY), True)

    def __show_access_granted(self):
        self.__device.write(
            Channel.LCD,
            'Access Granted'.center(maximum_lcd_characters, ' '),
        )

    def __show_green_led(self):
        self.__device.write(Channel.LED, False, True, False)

    def __start_logout_timer(self):
        self.__cancel_logout_timer()
        self.__logout_timer = threading.Timer(
            logout_timer_interval_seconds,
            self.__logout_timer_tick
        )
        self.__logout_timer.start()

    def __logout_timer_tick(self):
        if not self.__should_exit:
            remaining_seconds = self.__user_info.get('remaining_seconds')

            if remaining_seconds <= 0:
                self.logout()
                return

            self.__user_info['remaining_seconds'] = (remaining_seconds - logout_timer_interval_seconds)
            self.__show_remaining_time()
            self.__start_logout_timer()

    def __show_remaining_time(self):
        remaining_seconds = self.__user_info.get('remaining_seconds')
        if remaining_seconds < 300:
            self.__toggle_red_led()

        m, s = divmod(int(remaining_seconds), 60)
        h, m = divmod(m, 60)
        self.__device.write(
            Channel.LCD,
            'Remaining Time'.center(maximum_lcd_characters, ' '),
            '{0:02d}:{1:02d}:{2:02d}'.format(h, m, s).center(maximum_lcd_characters, ' ')
        )

    def __toggle_red_led(self):
        red_led_status = self.__device.read(Channel.PIN, self.__opts.get(ClientOption.PIN_LED_RED))
        self.__device.write(Channel.LED, not red_led_status, False, False)

    def __cancel_logout_timer(self):
        if self.__logout_timer:
            self.__logout_timer.cancel()

        self.__logout_timer = None

    def __extend_sesssion(self):
        self.__cancel_logout_timer()
        # TODO: add api call to let server know that time has been extended...

        session_seconds = self.__user_info.get('session_seconds')
        remaining_seconds = self.__user_info.get('remaining_seconds')
        remaining_extensions = self.__user_info.get('remaining_extensions')

        if remaining_extensions:
            if remaining_extensions != float('inf'):
                self.__user_info['remaining_extensions'] = remaining_extensions - 1

            remaining_seconds = remaining_seconds + session_seconds
            self.__user_info['remaining_seconds'] = remaining_seconds
            self.__logger.info('Session extended %s remaining_seconds', remaining_seconds)

            self.__show_session_extended()
        else:
            self.__show_no_extensions_remaining()

        self.__start_logout_timer()

    #
    #  A login attempt was made, and the user is was not authorized to use the machine,
    #

    def __show_access_denied(self):
        self.__show_red_led()
        self.__device.write(
            Channel.LCD,
            'Access Denied'.center(maximum_lcd_characters, ' '),
            'Take the class'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(2)
        self.__ensure_idle()

    def __show_red_led(self):
        self.__device.write(Channel.LED, True, False, False)

    def __show_session_extended(self):
        self.__device.write(
            Channel.LCD,
            'Session Extended'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(1)
        self.__show_remaining_time()

    def __show_no_extensions_remaining(self):
        self.__device.write(
            Channel.LCD,
            'No Extensions'.center(maximum_lcd_characters, ' '),
            'Remaining...'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(2)
        self.__show_remaining_time()

    #
    # training - the client has entered training mode
    #

    def __show_in_training(self):
        self.__cancel_logout_timer()
        self.__show_blue_led()

        # TODO: if the current user is not a trainer, prompt for
        # a training badge...
        # else

        # TODO: if the current user is a trainer...
        self.__device.write(
            Channel.LCD,
            'Training Mode'.center(maximum_lcd_characters, ' '),
            'Scan Badge...'.center(maximum_lcd_characters, ' ')
        )

    def __register_user(self, *args, **kwargs):

        #TODO need to ensure we have a trainer id...

        badge_code = kwargs.get('badge_code')
        self.__logger.debug('Register User: %s', badge_code)

    #
    # Stop - The client has received a stop command
    #

    def __handle_stop_command(self, **kwargs):
        self.__stop()

    def __stop(self):
        # what if device is in use, should stop return error, or forcefully do a stop?
        # TODO: wait for client status(self.state) to be done before we exit...
        # i.e. logout should be complete etc...

        self.__ensure_idle()
        self.__device.stop()
        self.__exit()

    def __exit(self):
        self.__should_exit = True

    #
    # Status - The client has received a status command
    #

    def __handle_status_command(self, **kwargs):
        return self.state

    def is_authorized(self, *args, **kwargs):
        return self.__do_login(*args, **kwargs)

    def is_waiting_for_training(self, *args, **kwargs):
        current = time.time()
        while not self.__should_exit and self.__device.read(Channel.PIN, self.__opts.get(ClientOption.PIN_LOGOUT)) \
                and time.time() - current < training_mode_delay_seconds:
            time.sleep(0.5)

        return self.__device.read(Channel.PIN, self.__opts.get(ClientOption.PIN_LOGOUT))

    def is_current_badge_code(self, *args, **kwargs):
        new_badge_code = kwargs.get('badge_code')
        current_badge_code = self.__user_info.get('badge_code') if self.__user_info else None

        if current_badge_code and current_badge_code == new_badge_code:
            self.__extend_sesssion()
            return True

        return False

    # noinspection PyPep8Naming
    def on_enter_IDLE(self, *args, **kwargs):
        self.__ensure_idle()
        self.__show_scan_badge()

    # noinspection PyPep8Naming
    def on_enter_IN_FAULT(self):
        self.__device.fault()

    # noinspection PyPep8Naming
    def on_enter_IN_USE(self, *args, **kwargs):
        self.__ensure_in_use()
        self.__start_logout_timer()

    def on_enter_IN_TRAINING(self, *args, **kwargs):
        self.__cancel_logout_timer()
        self.__show_in_training()

    def __run(self):
        opts = self.__opts

        #TODO: add try/catch to ensure self.__stop() is called before exiting the context block
        # on interrupts like CTRL-C which is used during debug mode
        with RemoteCommandHandler() as handler, DeviceApi(opts) as device:
            self.__device = device

            handler.on(Command.STOP, self.__handle_stop_command)
            handler.on(Command.STATUS, self.__handle_status_command)
            handler.listen()

            def handle_badge_code(*args, **kwargs):
                if self.state is State.IN_TRAINING:
                    self.__register_user(*args, **kwargs)
                else:
                    self.login(*args, **kwargs)

            device.on(
                Channel.SERIAL,
                direction=device.GPIO.IN,
                call_back=handle_badge_code
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

            except (KeyboardInterrupt, SystemExit):
                self.__exit()

            except Exception as e:
                self.set_state(State.IN_FAULT)
                self.__logger.debug('%s failed.', PackageInfo.pip_package_name)
                self.__logger.exception(e)

            if not self.__should_exit:
                self.__logger.debug('Retrying in 5 seconds...')
                time.sleep(3)
                self.set_state(State.INITIALIZED)


#TODO
    # finally:
    #     logging.shutdown()