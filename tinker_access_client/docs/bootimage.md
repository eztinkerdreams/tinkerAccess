## Creating a tinker-access-client boot image:

This document details the steps required to create a [Raspbian OS](https://www.raspberrypi.org/downloads/raspbian/) boot image and prepare it for the tinker-access-client.

There are many such guides that you can find, some with much more info, some with much less. I will let you pick your own poison, but its hard to be [this](https://www.raspberrypi.org/documentation/installation/installing-images/README.md) guide.

The intent of this guid it to document a couple of additional steps that were not immediately apparent to me after I had the image.

1. A the root of the boot image add an empty .ssh file, this will automatically enable the ssh service wich is disabled by default.

2. Unpack
