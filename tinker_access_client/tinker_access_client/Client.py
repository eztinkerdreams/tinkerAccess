import os
import time
import logging
import threading
from transitions import Machine

from Command import Command
from TinkerAccessServerApi import TinkerAccessServerApi
from PackageInfo import PackageInfo
from DeviceApi import DeviceApi, Channel
from RemoteCommandHandler import RemoteCommandHandler
from ClientOptionParser import ClientOptionParser, ClientOption
from UserRegistrationException import UserRegistrationException
from UnauthorizedAccessException import UnauthorizedAccessException

maximum_lcd_characters = 15
training_mode_delay_seconds = 2
logout_timer_interval_seconds = 1


class State(object):
    INITIALIZED = 'initialized'
    IDLE = 'idle'
    IN_USE = 'in_use'
    IN_TRAINING = 'in_training'
    TERMINATED = 'terminated'


class Trigger(object):
    IDLE = 'idle'
    LOGIN = 'login'
    LOGOUT = 'logout'
    TERMINATE = 'terminate'


class Client(Machine):
    def __init__(self, device=None):
        self.__device = device
        self.__user_info = None
        self.__logout_timer = None
        self.__logger = logging.getLogger(__name__)
        self.__opts = ClientOptionParser().parse_args()[0]
        self.__tinkerAccessServerApi = TinkerAccessServerApi(self.__opts)

        states = []
        for key, value in vars(State).items():
            if not key.startswith('__'):
                states.append(value)

        transitions = [
            {
                'source': [State.INITIALIZED],
                'trigger': Trigger.IDLE,
                'dest': State.IDLE
            },

            {
                'source': [State.IDLE],
                'trigger': Trigger.LOGIN,
                'dest': State.IN_USE,
                'conditions': ['is_authorized']
            },

            {
                'source': [State.IN_USE],
                'trigger': Trigger.LOGIN,
                'dest': State.IN_USE,
                'conditions': ['is_current_badge_code']
            },

            {
                'source': [State.IN_USE, State.IN_TRAINING],
                'trigger': Trigger.LOGOUT,
                'dest': State.IDLE
            },

            {
                'source': [State.IDLE],
                'trigger': Trigger.LOGOUT,
                'dest': State.IN_TRAINING,
                'conditions': ['is_waiting_for_training']
            },

            {
                'source': '*',
                'trigger': Trigger.TERMINATE,
                'dest': State.TERMINATED
            }
        ]

        Machine.__init__(self, queued=True, states=states,
                         transitions=transitions, initial=State.INITIALIZED, after_state_change='update_status')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

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

        # TODO: this should block until power sense returns false, with a max timeout using logout_coast_time
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
            self.__show_attempting_login(1)
            self.__update_user_context(
                self.__tinkerAccessServerApi.login(badge_code)
            )
            remaining_seconds = self.__user_info.get('remaining_seconds')
            self.__show_access_granted(1)

        except UnauthorizedAccessException:
            self.__show_access_denied(2)
            self.__ensure_idle()

        return self.__user_info is not None

    def __show_attempting_login(self, delay=0):
        self.__device.write(
            Channel.LCD,
            'Attempting'.center(maximum_lcd_characters, ' '),
            'Login...'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(delay)

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

    def __show_access_granted(self, delay=0):
        self.__device.write(
            Channel.LCD,
            'Access Granted'.center(maximum_lcd_characters, ' '),
        )
        time.sleep(delay)

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
        if not self.is_terminated() and self.__user_info:
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

            self.__show_session_extended(1)
        else:
            self.__show_no_extensions_remaining(2)

        self.__start_logout_timer()

    #
    #  A login attempt was made, and the user is was not authorized to use the machine,
    #

    def __show_access_denied(self, delay=0):
        self.__show_red_led()
        self.__device.write(
            Channel.LCD,
            'Access Denied'.center(maximum_lcd_characters, ' '),
            'Take the class'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(delay)

    def __show_red_led(self):
        self.__device.write(Channel.LED, True, False, False)

    def __show_session_extended(self, delay=0):
        self.__device.write(
            Channel.LCD,
            'Session Extended'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(delay)
        self.__show_remaining_time()

    def __show_no_extensions_remaining(self, delay=0):
        self.__device.write(
            Channel.LCD,
            'No Extensions'.center(maximum_lcd_characters, ' '),
            'Remaining...'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(delay)
        self.__show_remaining_time()

    #
    # training - the client has entered training mode
    #

    def __show_training_mode_activated(self, delay=0):
        self.__device.write(
            Channel.LCD,
            'Training Mode'.center(maximum_lcd_characters, ' '),
            'Activated...'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(delay)

    def __show_scan_trainer_badge(self):
        self.__device.write(
            Channel.LCD,
            'Scan'.center(maximum_lcd_characters, ' '),
            'Trainer Badge...'.center(maximum_lcd_characters, ' ')
        )

    def __activate_trainer(self, badge_code):
        # Note: currently we call the normal login method on the tinkerAccessServer
        # the backend ensures the user is a trainer on the 'registerUser' call.
        # I expect this might change in the future once the server code gets refactored
        try:
            self.__show_attempting_login(1)
            self.__update_user_context(
                self.__tinkerAccessServerApi.login(badge_code)
            )
            self.__show_trainer_accepted(1)
            self.__show_scan_student_badge()

        except UnauthorizedAccessException:
            self.__show_access_denied(2)
            self.__show_scan_trainer_badge()

        return self.__user_info is not None

    def __show_trainer_accepted(self, delay=0):
        self.__device.write(
            Channel.LCD,
            'Trainer'.center(maximum_lcd_characters, ' '),
            'Accepted...'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(delay)

    def __show_scan_student_badge(self, delay=0):
        self.__device.write(
            Channel.LCD,
            'Scan'.center(maximum_lcd_characters, ' '),
            'Student Badge...'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(delay)

    def __register_student(self, badge_code):
        try:
            self.__show_attempting_registration(1)
            trainer_id = self.__user_info.get('user_id')
            trainer_badge_code = self.__user_info.get('badge_code')
            self.__tinkerAccessServerApi.register_user(trainer_id, trainer_badge_code, badge_code)
            self.__show_student_registered(1)

        except UserRegistrationException:
            self.__show_access_denied(2)

        self.__show_scan_student_badge()
        self.__show_blue_led()

    def __show_attempting_registration(self, delay=0):
        self.__device.write(
            Channel.LCD,
            'Attempting'.center(maximum_lcd_characters, ' '),
            'Registration...'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(delay)

    def __show_student_registered(self, delay=0):
        self.__device.write(
            Channel.LCD,
            'Student'.center(maximum_lcd_characters, ' '),
            'Registered...'.center(maximum_lcd_characters, ' ')
        )
        time.sleep(delay)

    #
    # a badge code has been detected on the serial input
    #

    def handle_badge_code(self, *args, **kwargs):
        badge_code = kwargs.get('badge_code')
        # TODO: refactor to just pass badge_code as an argument
        if self.state is State.IN_TRAINING:
            if not self.__user_info:
                if self.__activate_trainer(badge_code):
                    self.__show_scan_student_badge()
                else:
                    self.__show_scan_trainer_badge()
            else:
                self.__register_student(badge_code)
        else:
            self.login(*args, **kwargs)


    #
    # wait - wait for the next edge detection event from the device.
    #

    def wait(self):
        self.__device.wait()

    #
    # status - The client has received a status command
    #

    def status(self):
        return self.state

    def update_status(self, *args, **kwargs):
        status_file = self.__opts.get(ClientOption.STATUS_FILE)
        with open(status_file, 'w') as f:
            f.write('{0}\n'.format(self.status()))
    #
    # conditions - used to allow/prevent triggers causing a transition if the conditions are not met.
    #

    def is_terminated(self):
        return self.state is State.TERMINATED

    def is_authorized(self, *args, **kwargs):
        return self.__do_login(*args, **kwargs)

    def is_waiting_for_training(self, *args, **kwargs):

        current = time.time()
        while not self.is_terminated() and self.__device.read(Channel.PIN, self.__opts.get(ClientOption.PIN_LOGOUT)) \
                and time.time() - current < training_mode_delay_seconds:
            time.sleep(0.1)

        return self.__device.read(Channel.PIN, self.__opts.get(ClientOption.PIN_LOGOUT))

    def is_current_badge_code(self, *args, **kwargs):
        new_badge_code = kwargs.get('badge_code')
        current_badge_code = self.__user_info.get('badge_code') if self.__user_info else None

        if current_badge_code and current_badge_code == new_badge_code:
            self.__extend_sesssion()
            return True

        return False

    #TODO states and method names to lower case

    # noinspection PyPep8Naming
    def on_enter_idle(self, *args, **kwargs):
        self.__ensure_idle()
        self.__show_scan_badge()

    # noinspection PyPep8Naming
    def on_enter_in_use(self, *args, **kwargs):
        self.__ensure_in_use()
        self.__start_logout_timer()

    # noinspection PyPep8Naming
    def on_enter_in_training(self, *args, **kwargs):
        self.__ensure_idle()
        self.__show_training_mode_activated(1)
        self.__show_scan_trainer_badge()

    # noinspection PyPep8Naming
    def on_enter_terminated(self, *args, **kwargs):
        self.__ensure_idle()

    @staticmethod
    def run(opts, args):
        should_exit = False
        logger = logging.getLogger(__name__)

        while not should_exit:
            try:
                with DeviceApi(opts) as device, \
                        Client(device) as client:

                # , \
                #         RemoteCommandHandler() as handler:
                #
                #     handler.on(Command.STOP, client.terminate)
                #     handler.on(Command.STATUS, client.status)
                #     handler.listen()

                    device.on(
                        Channel.SERIAL,
                        direction=device.GPIO.IN,
                        call_back=client.handle_badge_code
                    )

                    device.on(
                        Channel.PIN,
                        pin=opts.get(ClientOption.PIN_LOGOUT),
                        direction=device.GPIO.RISING,
                        call_back=client.logout
                    )

                    client.idle()
                    while not client.is_terminated():
                        logger.debug('%s is waiting...', PackageInfo.pip_package_name)
                        client.wait()
                    should_exit = True

            except (KeyboardInterrupt, SystemExit):
                should_exit = True

            except Exception as e:
                logger.exception(e)
                logger.debug('Retrying in 5 seconds...')
                time.sleep(5)

        status_file = opts.get(ClientOption.STATUS_FILE)
        if os.path.isfile(status_file):
            os.remove(status_file)
        logging.shutdown()
