#!/usr/bin/env python

# Reference: https://wiki.debian.org/LSBInitScripts

### BEGIN INIT INFO
# Provides:          tinker-access-client
# Required-Start:    $all
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: tinker-access-client
# Description:       The tinker-access-client service is responsible for coordinating communication
# between RPi's modules (i.e. RFID reader, LCD, power relays etc..) and the remote tinker_access_server.
### END INIT INFO

import os
import sys
import logging
from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
from ClientDaemon import ClientDaemon
from CommandHandler import CommandHandler
from ClientOptionParser import ClientOptionParser, Command


def run():
    if os.geteuid() != 0:
        sys.stdout.write(
            'You need to have root privileges to run {0} commands.\n'
            'Please try again, this time using \'sudo\'.\n'.format(PackageInfo.pip_package_name))
        sys.stdout.flush()
        sys.exit(1)

    (opts, args) = ClientOptionParser().parse_args()
    logger = ClientLogger.setup(opts)

    try:
        with CommandHandler(opts, args) as handler:
            handler.on(Command.STOP, ClientDaemon.stop)
            handler.on(Command.START, ClientDaemon.start)
            handler.on(Command.STATUS, ClientDaemon.status)
            handler.on(Command.UPDATE, ClientDaemon.update)
            handler.on(Command.REMOVE, ClientDaemon.remove)
            handler.on(Command.RESTART, ClientDaemon.restart)
            return handler.handle_command()

    except Exception as e:
        logger.exception(e)
        sys.stdout.write(str(e))
        sys.stdout.flush()
        sys.exit(1)

    finally:
        logging.shutdown()

if __name__ == '__main__':
    run()
