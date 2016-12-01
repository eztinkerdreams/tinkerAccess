# tinker-access-client

The tinker-access-client is a [Raspberry Pi](https://www.raspberrypi.org/products/) based access control system that can be used to prevent unauthorized users from using devices that require special training, it could also conceivable be used to control electronic lock boxes, or doors.

The system was originally designed and created by [Matt Stallard](https://github.com/mstallard) & [Matt Peopping](https://github.com/analogpixel) for [TinkerMill](http://www.tinkermill.org) a makerspace in [Longmont, CO](https://www.google.com/maps/place/Longmont,+CO/@40.1679379,-105.1678944,12z/data=!3m1!4b1!4m5!3m4!1s0x876bf908d5cc3349:0xc17da1eef3a32735!8m2!3d40.1672068!4d-105.1019275). It is continually being maintained and enhanced by other contributors in the community.

The client software is a [Python 2.7](https://www.python.org/download/releases/2.7/) service designed to run on the [Raspbian OS](https://www.raspberrypi.org/downloads/raspbian/). The service is responsible for coordinating activity between the RPi's peripherals (i.e. RFID reader, LCD, etc..) and the GPIO, as well as communicating with the [tinker-access-server](../tinker_access_server/README.md) for activity logging, authentication & authorization.

Official releases of the client software are packaged and published to [PyPI - the Python Package Index ](https://pypi.python.org/pypi/tinker-access-client/)

## Prerequisites:
- Build the custom [Raspberry Pi HAT](https://www.raspberrypi.org/blog/introducing-raspberry-pi-hats/) as described [here](../../docs/RFID_Wiring.pdf).

- Create a [Raspbian OS](https://www.raspberrypi.org/downloads/raspbian/) boot image as described [here](../docs/bootimage.md)

## Upgrade PIP:

**IMPORTANT**: If you have just created a new image using the previous mentioned guide, or you are using an existing image...

Ensure you have the latest version of [PIP](https://pip.pypa.io/en/stable) and its related setuptools installed, if you don't complete this step, you will almost certainly __not__ have a good time. Version issues with PIP and its related setuptools can be inconsistent, confusing and difficult to resolve, it is better to just avoid it now and ensure that they are updated.

You will find many ways describing how to do this [here](https://pip.pypa.io/en/stable/installing/)...
This is what has worked for me consistently:
```commandline
sudo pip --upgrade pip
```

## Installation:

By default, the tinker-access-client is installed as a service that starts immediately, as well as upon reboot of the device.

Install the latest version of the client & query its status.  
If all goes as planned, the expected output should be *'idle'*:

```commandline
sudo pip install tinker-access-client
sudo tinker-access-client status
```

TODO: screenshot...

If you didn't get the expected output, see the [troubleshooting guide](../docs/troubleshooting.md).

See the [development guide](../docs/development.md) for special installation instructions, best practices and other helpful information you can use for maintaining & enhancing the code for the future.

## Command-Line Tools:
The remaining information in this guide explains some ways to customize the behavior of the client, control the client, and/or get feedback about the state of the client
```
tinker-access-client --help
```
TOOD: screenshot

TODO: other examples...
