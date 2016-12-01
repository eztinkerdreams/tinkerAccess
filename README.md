![taicon](/taicon.png)

# tinkerAccess
The tinkerAccess system is a Raspberry Pi based access control system that can be used to prevent unauthorized users from using devices that require special training, it could also conceivable be used to control electronic lock boxes, or doors.

The system was originally designed and created by Matt Stallard, Ron Thomas, and Matt Peopping for TinkerMill a makerspace in Longmont, CO. It is continually being maintained and enhanced by other contributors in the community.

### Install the tinkerAccess system

There are two main components to the system. The [tinker-access-server](/tinker_access_server/README.md) & the [tinker-access-client](/tinker_access_client/README.md).  

If you intend to use both server & client on the same device, you can follow these simple instructions.

From the Rasbian terminal:

```
git clone https://github.com/TinkerMill/tinkerAccess.git
cd tinkerAccess
sudo bash
./install.sh
```

Additional specific information regarding the operation and configuration of each componemnt can be found here:

- [tinker-access-server](/tinker_access_server/README.md) 
- [tinker-access-client](/tinker_access_client/README.md)