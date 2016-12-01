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

from TinkerAccessClient import TinkerAccessClient

if __name__ == '__main__':
    TinkerAccessClient().run()
