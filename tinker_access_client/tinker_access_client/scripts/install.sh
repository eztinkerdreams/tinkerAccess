#!/usr/bin/env bash

#TOOD: ServiceInstall.py could just handle all of this, so we don't have a mix of bash/python
#and then it could also have unit test coverage

if [ "$EUID" -ne 0 ]; then
  echo "sudo required, try \"sudo bash ${BASH_SOURCE} ${@}\""
  exit 1
fi

python_package_name="tinker_access_client"
pip_package_name="${python_package_name//_/-}"
scripts_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
service_src="${scripts_dir}/../Service.py"
service_dest="/etc/init.d/${pip_package_name}"

#grant execute permission on the service script
chmod 755 "${service_src}"

#remove the existing service if it is a file or directory, and it is not a symlink
if [ -f "${service_dest}" ] || [ -d "${service_dest}" ] && [ ! -L "${service_dest}" ]; then
    rm -rfv "${service_dest}"
fi

#remove the existing service if it is a symlink and it is not pointed to the current target
if [ -L "${service_dest}" ] && [ "$( readlink "${service_dest}" )" != "${service_src}" ]; then
    rm -rfv "${service_dest}"
fi

#add the new service symlink if it doesn't already exists
#Note: using the -f options to overwrite this link can cause a "systemctl: 'daemon-reload' warning"
if [ ! -L "${service_dest}" ]; then
    ln -sv "${service_src}" "${service_dest}"
fi

#set the service to start on boot, and restart it
if hash update-rc.d 2>/dev/null; then
    update-rc.d "${pip_package_name}" defaults 91
fi

#restart/reload the service
if hash service 2>/dev/null; then
    service "${pip_package_name}" restart
fi