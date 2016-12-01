
#TODO: more please...
For development purposes the The client can be installed from many different types of locations (.i.e. the local file system and other [GitHub](https://github.com) branches), you can find additional examples [here](http://www.developerfiles.com/pip-install-from-local-git-repository/).

You can use the [-e, --editable ](https://pip.pypa.io/en/latest/reference/pip_install/#cmdoption-e) flag to install the package in editable mode. This will create a symlink from site_packages to your local development directory so you don't need to re-install each time you change a file.
```commandline
sudo pip install -e local_path/setup.py
```

##### Run in stand-alone mode:

You can run the client as a stand alone script if you don't want to install a full blown service. This is helpful for testing and development purposes.


### Testing:

See the [README](../tinker_access_client/tests/README.md) for more info.

### Logging:


TODO: ...