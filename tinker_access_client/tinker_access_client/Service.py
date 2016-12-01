#!/usr/bin/env python

### BEGIN INIT INFO
# Provides:          tinker-access-client
# Required-Start:    $remote_fs $syslog $network
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: tinker-access-client
# Description:       The tinker-access-client service is responsible for coordinating communication
# between RPi's modules (i.e. RFID reader, LCD, power relays etc..) and the remote tinker_access_server.
### END INIT INFO

import sys
import logging
from ClientDaemon import ClientDaemon
from ClientOption import ClientOption
from CommandHandler import CommandHandler
from ClientOptionParser import ClientOptionParser, Command


def run():
    (opts, args) = ClientOptionParser().parse_args()

    try:

        # TODO: whats the best place to handle this configuration of the logger?
        sys_log_format = \
            '%(asctime)s %(hostname)s %(app_id)s %(version)s %(device_id)s %(device_name)s ' \
            '%(user_id)s %(user_name)s %(badge_code)s %(message)s'

        logging.basicConfig(
            datefmt='%FT%T',
            level=logging.DEBUG,
            format='%(asctime)s %(message)s',
            filename=opts.get(ClientOption.LOG_FILE)
        )

        with CommandHandler(opts, args) as handler:
            handler.on(Command.STOP, ClientDaemon.stop)
            handler.on(Command.START, ClientDaemon.start)
            handler.on(Command.STATUS, ClientDaemon.status)
            handler.on(Command.RESTART, ClientDaemon.restart)
            return handler.handle_command()

    except Exception as e:
        sys.stdout.write(str(e))
        sys.stdout.flush()
        sys.exit(1)

    finally:
        logging.shutdown()

if __name__ == '__main__':
    run()
