# tinker_access_client

The tinker_access_client runs on RPi devices attached to machines that required training at the [TinkerMill](http://www.tinkermill.org)

The client software is responsible for coordinating communication between RPi's modules (i.e. RFID reader, LCD, power relays etc..) and the remote tinker_access_server.

The device also allows for trainers to register users after completing a class by entering 'training' mode and scanning the users RFID badges.

Training mode can be entered by scanning the trainers RFID badge and then holding down the power reset button for continually for 3 seconds.
### Installation:

Ensure you have the latest version of PIP installed:

```commandline
sudo easy_install --upgrade pip
```

Install the latest version of the client:
```commandline
sudo pip install --upgrade tinker-access-client 
```

For development purposes the The client can be installed from many different types of locations (.i.e. the local file system and other [GitHub](https://github.com) branches), you can find additional examples [here](http://www.developerfiles.com/pip-install-from-local-git-repository/).

You can use the [-e, --editable ](https://pip.pypa.io/en/latest/reference/pip_install/#cmdoption-e) flag to install the package in editable mode. This will create a symlink from site_packages to your local development directory so you don't need to re-install each time you change a file.
```commandline
sudo pip install -e <local_path>/setup.py 
```

#### Command-Line:
The package installs a few command-line utilities, there is no need to prefix your commands with python.

##### Run in stand-alone mode:

You can run the client as a stand alone script if you don't want to install a full blown service. This is helpful for testing and development purposes.

The following options can be used to customize the behavior of the client. These options can be provided via the command line or a config file.
```
tinker-access-client --help
```

```
Usage: 
tinker-access-client command [options]

command:

        status : status desc...
        start : start desc...
        stop : stop desc...
        update : update...
        reload : reload...
        restart : restart...
        force_reload : force_reload...

TinkerMill Raspberry Pi access control system.

Examples:

  Start the client with the device id set to 'plasma-cutter'.
  If the client were to stop unexpectedly, a restart would be attempted every 5 seconds.
  The restart attempts would continue until the client stated successfully and continued to run for least 10 seconds.

  'tinker_access_client --device-id=plasma-cutter --restart-delay=5 --max-restart-attempts=inf --minimum-up-time=10' 

  Start the client configured to use a different tinker-access-server (i.e. a development server) and an alternative serial port

  'tinker_access_client --server-address=http://<server-address> --serial-port-name=/dev/ttyUSB1' 

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --config-file=CONFIG_FILE
                        the location of the config file to use [default:'/etc
                        /tinker-access-client.conf'] a non-default command-
                        line option value will have precedence over a config-
                        file option value
  --debug               run in foreground(a.k.a debug mode) [default:'False']
  --log-file=LOG_FILE   the path and name of the log file [default:'/var/log
                        /tinker-access-client.log']
  --pid-file=PID_FILE   the path & name of the pid file [default:'/var/run
                        /tinker-access-client.pid']
  --log-level=LOG_LEVEL
                        the log level to use [default:10]
  --server-address=SERVER_ADDRESS
                        the api's server address
                        [default:'http://10.2.1.2:5000']
  --device-id=DEVICE_ID
                        the device id for this client [default:0]
  --log-address-for-paper-trail=LOG_ADDRESS_FOR_PAPER_TRAIL
                        the log address for paper trail [default:none]

  Resilience:
    --restart-delay=RESTART_DELAY
                        seconds to wait before attempting to re-start after a
                        failure [default:3]
    --max-restart-attempts=MAX_RESTART_ATTEMPTS
                        the maximum number of times to attempt to re-start the
                        client in the case that it quits unexpectedly
                        [default:inf]
    --minimum-up-time=MINIMUM_UP_TIME
                        the minimum number of seconds that the client must be
                        running before considering it to have successfully
                        started [default:5]
    --logout-coast-time=LOGOUT_COAST_TIME
                        the maximum number of seconds to allow the physical
                        machine to power down after logout [default:7]

  RPi GPIO:
    --pin-logout=PIN_LOGOUT
                        the logout pin [default:16]
    --pin-power-relay=PIN_POWER_RELAY
                        the power relay pin [default:17]
    --pin-led-red=PIN_LED_RED
                        the red led pin [default:21]
    --pin-led-green=PIN_LED_GREEN
                        the green led pin [default:19]
    --pin-led-blue=PIN_LED_BLUE
                        the blue led pin [default:20]
    --pin-current-sense=PIN_CURRENT_SENSE
                        the current sense pin [default:12]

  SERIAL:
    --serial-port-name=SERIAL_PORT_NAME
                        the serial port name to use [default:'/dev/ttyUSB0']
    --serial-port-speed=SERIAL_PORT_SPEED
                        the serial port speed to use [default:9600]

```

###### Examples:


Start the client with the device id set to 'plasma-cutter'.
If the client were to stop unexpectedly, a restart would be attempted every 5 seconds.
The restart attempts would continue until the client stated successfully and continued
to run for least 10 seconds.
```
tinker-access-client --device-id=plasma-cutter --restart-delay=5 \
    --max-restart-attempts=inf --minimum-up-time=10
```
Start the client configured to use a different tinker-access-server (i.e. a development server)
and an alternative serial port
```
tinker-access-client --server-address=http://<server-address> --serial-port-name=/dev/ttyUSB1'
```

##### Run as a service:

TODO: ...

### Testing:

See the [README](../tinker_access_client/tests/README.md) for more info.

### Logging:

TODO: ...
