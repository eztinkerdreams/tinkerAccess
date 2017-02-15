import os
import sys
import ConfigParser
from optparse import OptionParser, OptionGroup

from Command import Command
from PackageInfo import PackageInfo
from ClientOption import ClientOption

ClientOptionDefaults = {
    ClientOption.DEBUG: False,
    ClientOption.LOG_LEVEL: 40,
    ClientOption.PIN_LOGOUT: 16,
    ClientOption.PIN_LED_RED: 21,
    ClientOption.DEVICE_ID: None,
    ClientOption.PIN_LED_BLUE: 20,
    ClientOption.RESTART_DELAY: 5,
    ClientOption.PIN_LED_GREEN: 19,
    ClientOption.PIN_POWER_RELAY: 17,
    ClientOption.FORCE_UPDATE: False,
    ClientOption.LOGOUT_COAST_TIME: 0,
    ClientOption.PIN_CURRENT_SENSE: 12,
    ClientOption.SERIAL_PORT_SPEED: 9600,
    ClientOption.MAX_POWER_DOWN_TIMEOUT: 5,
    ClientOption.SERIAL_PORT_NAME: '/dev/ttyUSB0',
    ClientOption.SERVER_ADDRESS: 'http://10.2.1.2:5000',
    ClientOption.CONFIG_FILE: '/etc/{0}.conf'.format(PackageInfo.pip_package_name),
    ClientOption.PID_FILE: '/var/run/{0}.pid'.format(PackageInfo.pip_package_name),
    ClientOption.LOG_FILE: '/var/log/{0}.log'.format(PackageInfo.pip_package_name),
    ClientOption.STATUS_FILE: '/var/log/{0}.status'.format(PackageInfo.pip_package_name),
    ClientOption.LOGGING_CONFIG_FILE: '/etc/{0}.logging.conf'.format(PackageInfo.pip_package_name)
}


class ClientOptionParser(object):
    def __init__(self, phase=None):
        self.__phase = phase
        self.__parser = OptionParser(
            version='%prog v{0}'.format(PackageInfo.version) if PackageInfo.version is not None else None)

        if phase == 'install':
            for arg in sys.argv:
                if str(arg).startswith('-'):
                    self.__parser.add_option(str(arg).split('=', 1)[0])

        usage = "\n%prog command [options]"
        commands = ['\n\ncommand:\n']
        for key, value in vars(Command).items():
            if not key.startswith('__'):
                desc = value['description']
                cmd = value['command']
                commands.append('\t%s : %s' % (cmd, desc))
        commands = '\n'.join(commands)
        usage += commands
        usage += '\n\nTinkerMill Raspberry Pi access control system.' \
                 '\n\nExamples:\n\n' \
                 '  Start the client configured to use a different tinker-access-server ' \
                 '(i.e. a development server) and an alternative serial port' \
                 '\n\n  \'sudo {0} --server-address=http://<server-address> ' \
                 '--serial-port-name=/dev/ttyUSB1\' '.format(PackageInfo.python_package_name)

        self.__parser.set_usage(usage)

        self.__parser.add_option(
            '--config-file',
            help='the location of the config file to use [default:\'%default\'] '
                 'a non-default command-line option value will have precedence '
                 'over a config-file option value',
            default=ClientOptionDefaults[ClientOption.CONFIG_FILE],
            dest=ClientOption.CONFIG_FILE,
            action='store')

        self.__parser.add_option(
            '--logging-config-file',
            help='the location of a logging config file to use [default:\'%default\'] '
                 'If this file is present, it will override the default logging configuration '
                 'including the --log-level and --log-file options',
            default=ClientOptionDefaults[ClientOption.LOGGING_CONFIG_FILE],
            dest=ClientOption.LOGGING_CONFIG_FILE,
            action='store')

        self.__parser.add_option(
            '--debug',
            help='run in the foreground (a.k.a debug mode) [default:\'%default\']',
            default=ClientOptionDefaults[ClientOption.DEBUG],
            dest=ClientOption.DEBUG,
            action='store_true')

        self.__parser.add_option(
            '--force-update',
            help='This option will force the update command to do an update, even when the current version '
                 'is the latest version, or already matches the version specified in the update command'
                 ' [default:\'%default\']',
            default=ClientOptionDefaults[ClientOption.FORCE_UPDATE],
            dest=ClientOption.FORCE_UPDATE,
            action='store_true')

        self.__parser.add_option(
            '--log-file',
            help='the path and name of the log file [default:\'%default\']',
            default=ClientOptionDefaults[ClientOption.LOG_FILE],
            dest=ClientOption.LOG_FILE,
            action='store')

        self.__parser.add_option(
            '--status-file',
            help='the path and name of the status file, the contents of this file will always '
                 'reflect the current state of the client. (i.e. initialized, idle, in_use, in_training, terminated) '
                 'A missing file indicates the client is not running [default:\'%default\']',
            default=ClientOptionDefaults[ClientOption.STATUS_FILE],
            dest=ClientOption.STATUS_FILE,
            action='store')

        self.__parser.add_option(
            '--pid-file',
            help='the path & name of the pid file [default:\'%default\']',
            default=ClientOptionDefaults[ClientOption.PID_FILE],
            dest=ClientOption.PID_FILE,
            action='store')

        self.__parser.add_option(
            '--log-level',
            help='the log level to use [default:%default]',
            default=ClientOptionDefaults[ClientOption.LOG_LEVEL],
            dest=ClientOption.LOG_LEVEL,
            type='int',
            action='store')

        self.__parser.add_option(
            '--server-address',
            help='the api\'s server address [default:\'%default\']',
            default=ClientOptionDefaults[ClientOption.SERVER_ADDRESS],
            dest=ClientOption.SERVER_ADDRESS,
            action='store')

        self.__parser.add_option(
            '--device-id',
            help='A unique identity for this client [default:\'%default\']',
            default=ClientOptionDefaults[ClientOption.DEVICE_ID],
            dest=ClientOption.DEVICE_ID,
            action='store')

        self.__parser.add_option(
            '--logout-coast-time',
            help='a fixed number of seconds to wait for the physical machine '
                 'to stop after power has been disabled. '
                 '(i.e. a blade to stop spinning etc...) '
                 '[default:%default]',
            default=ClientOptionDefaults[ClientOption.LOGOUT_COAST_TIME],
            dest=ClientOption.LOGOUT_COAST_TIME,
            type='int',
            action='store')

        self.__parser.add_option(
            '--max-power-down-timeout',
            help='the maximum number of seconds to wait for the current sense pin to go low '
                 '[default:%default]',
            default=ClientOptionDefaults[ClientOption.MAX_POWER_DOWN_TIMEOUT],
            dest=ClientOption.MAX_POWER_DOWN_TIMEOUT,
            type='int',
            action='store')

        self.__parser.add_option(
            '--restart-delay',
            help='seconds to wait before attempting to re-start after a failure [default:%default]',
            default=ClientOptionDefaults[ClientOption.RESTART_DELAY],
            dest=ClientOption.RESTART_DELAY,
            type='int',
            action='store')

        gpio_group = OptionGroup(self.__parser, 'RPi GPIO')

        gpio_group.add_option(
            '--pin-logout',
            help='the logout pin [default:%default]',
            default=ClientOptionDefaults[ClientOption.PIN_LOGOUT],
            dest=ClientOption.PIN_LOGOUT,
            type='int',
            action='store')

        gpio_group.add_option(
            '--pin-power-relay',
            help='the power relay pin [default:%default]',
            default=ClientOptionDefaults[ClientOption.PIN_POWER_RELAY],
            dest=ClientOption.PIN_POWER_RELAY,
            type='int',
            action='store')

        gpio_group.add_option(
            '--pin-led-red',
            help='the red led pin [default:%default]',
            default=ClientOptionDefaults[ClientOption.PIN_LED_RED],
            dest=ClientOption.PIN_LED_RED,
            type='int',
            action='store')

        gpio_group.add_option(
            '--pin-led-green',
            help='the green led pin [default:%default]',
            default=ClientOptionDefaults[ClientOption.PIN_LED_GREEN],
            dest=ClientOption.PIN_LED_GREEN,
            type='int',
            action='store')

        gpio_group.add_option(
            '--pin-led-blue',
            help='the blue led pin [default:%default]',
            default=ClientOptionDefaults[ClientOption.PIN_LED_BLUE],
            dest=ClientOption.PIN_LED_BLUE,
            type='int',
            action='store')

        gpio_group.add_option(
            '--pin-current-sense',
            help='the current sense pin [default:%default]',
            default=ClientOptionDefaults[ClientOption.PIN_CURRENT_SENSE],
            dest=ClientOption.PIN_CURRENT_SENSE,
            type='int',
            action='store')

        self.__parser.add_option_group(gpio_group)

        serial_group = OptionGroup(self.__parser, 'SERIAL')

        serial_group.add_option(
            '--serial-port-name',
            help='the serial port name to use [default:\'%default\']',
            default=ClientOptionDefaults[ClientOption.SERIAL_PORT_NAME],
            dest=ClientOption.SERIAL_PORT_NAME,
            action='store')

        serial_group.add_option(
            '--serial-port-speed',
            help='the serial port speed to use [default:%default]',
            default=ClientOptionDefaults[ClientOption.SERIAL_PORT_SPEED],
            dest=ClientOption.SERIAL_PORT_SPEED,
            type='int',
            action='store')

        self.__parser.add_option_group(serial_group)

    def parse_args(self, args=None, values=None):
        (opts, args) = self.__parser.parse_args(args=args, values=values)
        items = vars(opts)

        options = self.__parser.option_list[:]
        for group in self.__parser.option_groups:
            options = options + group.option_list[:]

        if os.path.isfile(items.get(ClientOption.CONFIG_FILE)):
            config_file_parser = ConfigParser.RawConfigParser()
            config_file_parser.read(items.get(ClientOption.CONFIG_FILE))
            if config_file_parser.has_section('config'):
                for item in config_file_parser.items('config'):
                    option = next((i for i in options if i.dest == item[0]), None)
                    if option:
                        key = item[0]
                        value = item[1]
                        if option.type == 'int':
                            value = int(value)

                        if option.type == 'float':
                            value = float(value)

                        # prevents non-default command-line options from being replaced by config-file options
                        if items.get(key) == option.default != value:
                            items[key] = value

        # TODO: make args[0] required?, check the value and raise error parser.error()
        return items, args
