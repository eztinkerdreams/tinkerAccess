import sys
import os
import ConfigParser
from optparse import OptionParser, OptionGroup

from Command import Command
from PackageInfo import PackageInfo
from ClientOption import ClientOption

ClientOptionDefaults = {
    ClientOption.DEBUG: False,
    ClientOption.DEBUG_PORT: 2020,
    ClientOption.CONFIG_FILE: '/etc/{0}.conf'.format(PackageInfo.pip_package_name),
    ClientOption.PID_FILE: '/var/run/{0}.pid'.format(PackageInfo.pip_package_name),
    ClientOption.LOG_FILE: '/var/log/{0}.log'.format(PackageInfo.pip_package_name),
    ClientOption.LOG_LEVEL: 10,
    ClientOption.SERVER_ADDRESS: 'http://10.2.1.2:5000',
    ClientOption.DEVICE_ID: 0,
    ClientOption.SERIAL_PORT_NAME: '/dev/ttyUSB0',
    ClientOption.SERIAL_PORT_SPEED: 9600,
    ClientOption.PIN_LOGOUT: 16,
    ClientOption.CLIENT_PORT: 8089,
    ClientOption.PIN_POWER_RELAY: 17,
    ClientOption.PIN_LED_RED: 21,
    ClientOption.PIN_LED_GREEN: 19,
    ClientOption.PIN_LED_BLUE: 20,
    ClientOption.PIN_CURRENT_SENSE: 12,
    ClientOption.LOGOUT_COAST_TIME: 7,
    ClientOption.RESTART_DELAY: 3,
    ClientOption.MAX_RESTART_ATTEMPTS: float('inf'),
    ClientOption.MINIMUM_UP_TIME: 5,
    ClientOption.LOG_ADDRESS_FOR_PAPER_TRAIL: None
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
                 '  Start the client with the device id set to \'plasma-cutter\'.' \
                 '\n  If the client were to stop unexpectedly, a restart would be attempted every 5 seconds.' \
                 '\n  The restart attempts would continue until the client stated successfully' \
                 ' and continued to run for least 10 seconds.' \
                 '\n\n  \'{0} --device-id=plasma-cutter --restart-delay=5 --max-restart-attempts=inf ' \
                 '--minimum-up-time=10\' ' \
                 '\n\n  Start the client configured to use a different tinker-access-server ' \
                 '(i.e. a development server) and an alternative serial port' \
                 '\n\n  \'{0} --server-address=http://<server-address> ' \
                 '--serial-port-name=/dev/ttyUSB1\' '.format(PackageInfo.python_package_name)

        self.__parser.set_usage(usage)

        self.__parser.add_option('--config-file',
                          help='the location of the config file to use [default:\'%default\'] '
                               'a non-default command-line option value will have precedence '
                               'over a config-file option value',
                          default=ClientOptionDefaults[ClientOption.CONFIG_FILE],
                          dest=ClientOption.CONFIG_FILE,
                          action='store')

        self.__parser.add_option('--debug',
                          help='run in foreground(a.k.a debug mode) [default:\'%default\']',
                          default=ClientOptionDefaults[ClientOption.DEBUG],
                          dest=ClientOption.DEBUG,
                          action='store_true')

        self.__parser.add_option('--debug-port',
                         help='The port to host the virtual device UI in debug mode [default:\'%default\']',
                         default=ClientOptionDefaults[ClientOption.DEBUG_PORT],
                         dest=ClientOption.DEBUG_PORT,
                         type='int',
                         action='store')

        self.__parser.add_option('--client-port',
                                 help='The port to listen for external commands, i.e. (status, config, reload etc...)'
                                      ' [default:\'%default\']',
                                 default=ClientOptionDefaults[ClientOption.CLIENT_PORT],
                                 dest=ClientOption.CLIENT_PORT,
                                 type='int',
                                 action='store')

        self.__parser.add_option('--log-file',
                          help='the path and name of the log file [default:\'%default\']',
                          default=ClientOptionDefaults[ClientOption.LOG_FILE],
                          dest=ClientOption.LOG_FILE,
                          action='store')

        self.__parser.add_option('--pid-file',
                          help='the path & name of the pid file [default:\'%default\']',
                          default=ClientOptionDefaults[ClientOption.PID_FILE],
                          dest=ClientOption.PID_FILE,
                          action='store')

        self.__parser.add_option('--log-level',
                          help='the log level to use [default:%default]',
                          default=ClientOptionDefaults[ClientOption.LOG_LEVEL],
                          dest=ClientOption.LOG_LEVEL,
                          type='int',
                          action='store')

        self.__parser.add_option('--server-address',
                          help='the api\'s server address [default:\'%default\']',
                          default=ClientOptionDefaults[ClientOption.SERVER_ADDRESS],
                          dest=ClientOption.SERVER_ADDRESS,
                          action='store')

        self.__parser.add_option('--device-id',
                          help='the device id for this client [default:%default]',
                          default=ClientOptionDefaults[ClientOption.DEVICE_ID],
                          dest=ClientOption.DEVICE_ID,
                          action='store')

        self.__parser.add_option('--log-address-for-paper-trail',
                                 help='the log address for paper trail [default:%default]',
                                 default=ClientOptionDefaults[ClientOption.LOG_ADDRESS_FOR_PAPER_TRAIL],
                                 dest=ClientOption.LOG_ADDRESS_FOR_PAPER_TRAIL,
                                 action='store')

        resilience_group = OptionGroup(self.__parser, 'Resilience')

        resilience_group.add_option('--restart-delay',
                                    help='seconds to wait before attempting to re-start after a failure [default:%default]',
                                    default=ClientOptionDefaults[ClientOption.RESTART_DELAY],
                                    dest=ClientOption.RESTART_DELAY,
                                    type='int',
                                    action='store')

        resilience_group.add_option('--max-restart-attempts',
                                    help='the maximum number of times to attempt to re-start the client in the case '
                                         'that it quits unexpectedly [default:%default]',
                                    default=ClientOptionDefaults[ClientOption.MAX_RESTART_ATTEMPTS],
                                    dest=ClientOption.MAX_RESTART_ATTEMPTS,
                                    type='float',
                                    action='store')

        resilience_group.add_option('--minimum-up-time',
                                    help='the minimum number of seconds that the client must be running before considering '
                                         'it to have successfully started [default:%default]',
                                    default=ClientOptionDefaults[ClientOption.MINIMUM_UP_TIME],
                                    dest=ClientOption.MINIMUM_UP_TIME,
                                    type='int',
                                    action='store')

        resilience_group.add_option('--logout-coast-time',
                                    help='the maximum number of seconds to allow the physical machine '
                                         'to power down after logout [default:%default]',
                                    default=ClientOptionDefaults[ClientOption.LOGOUT_COAST_TIME],
                                    dest=ClientOption.LOGOUT_COAST_TIME,
                                    type='int',
                                    action='store')

        self.__parser.add_option_group(resilience_group)

        gpio_group = OptionGroup(self.__parser, 'RPi GPIO')

        gpio_group.add_option('--pin-logout',
                              help='the logout pin [default:%default]',
                              default=ClientOptionDefaults[ClientOption.PIN_LOGOUT],
                              dest=ClientOption.PIN_LOGOUT,
                              type='int',
                              action='store')

        gpio_group.add_option('--pin-power-relay',
                              help='the power relay pin [default:%default]',
                              default=ClientOptionDefaults[ClientOption.PIN_POWER_RELAY],
                              dest=ClientOption.PIN_POWER_RELAY,
                              type='int',
                              action='store')

        gpio_group.add_option('--pin-led-red',
                              help='the red led pin [default:%default]',
                              default=ClientOptionDefaults[ClientOption.PIN_LED_RED],
                              dest=ClientOption.PIN_LED_RED,
                              type='int',
                              action='store')

        gpio_group.add_option('--pin-led-green',
                              help='the green led pin [default:%default]',
                              default=ClientOptionDefaults[ClientOption.PIN_LED_GREEN],
                              dest=ClientOption.PIN_LED_GREEN,
                              type='int',
                              action='store')

        gpio_group.add_option('--pin-led-blue',
                              help='the blue led pin [default:%default]',
                              default=ClientOptionDefaults[ClientOption.PIN_LED_BLUE],
                              dest=ClientOption.PIN_LED_BLUE,
                              type='int',
                              action='store')

        gpio_group.add_option('--pin-current-sense',
                              help='the current sense pin [default:%default]',
                              default=ClientOptionDefaults[ClientOption.PIN_CURRENT_SENSE],
                              dest=ClientOption.PIN_CURRENT_SENSE,
                              type='int',
                              action='store')

        self.__parser.add_option_group(gpio_group)

        serial_group = OptionGroup(self.__parser, 'SERIAL')

        serial_group.add_option('--serial-port-name',
                                help='the serial port name to use [default:\'%default\']',
                                default=ClientOptionDefaults[ClientOption.SERIAL_PORT_NAME],
                                dest=ClientOption.SERIAL_PORT_NAME,
                                action='store')

        serial_group.add_option('--serial-port-speed',
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
