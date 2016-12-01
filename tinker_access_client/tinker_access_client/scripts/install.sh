#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]; then
  echo "sudo required, try \"sudo bash ${BASH_SOURCE} ${@}\""
  exit 1
fi

python_package_name="tinker_access_client"
pip_package_name="${python_package_name//_/-}"
scripts_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
update_script="${scripts_dir}/update.sh"
service_script="${scripts_dir}/../Service.py"
service_dest="/etc/init.d/${pip_package_name}"
echo "service_script ${service_script}"
echo "update_script ${update_script}"
#grant execute permission on the service script
chmod 755 "${update_script}"
chmod 755 "${service_script}"

#remove the existing service if it is a file or directory, and it is not a symlink
if [ -f "${service_dest}" ] || [ -d "${service_dest}" ] && [ ! -L "${service_dest}" ]; then
    sudo update-rc.d -f tinkerclient remove
    rm -rfv "${service_dest}"
fi

#remove the existing service if it is a symlink and it is not pointed to the current target
if [ -L "${service_dest}" ] && [ "$( readlink "${service_dest}" )" != "${service_script}" ]; then
    rm -rfv "${service_dest}"
fi

#add the new service symlink if it doesn't already exists
#Note: using the -f options to overwrite this link can cause a "systemctl: 'daemon-reload' warning"
if [ ! -L "${service_dest}" ]; then
    ln -sv "${service_script}" "${service_dest}"
fi

#set the service to start on boot, and restart it
if hash update-rc.d 2>/dev/null; then
    update-rc.d "${pip_package_name}" defaults 91
fi

#restart/reload the service
if hash service 2>/dev/null; then
    service "${pip_package_name}" restart
fi

#enable auto-updates
#crontab_name="${pip_package_name}-update"
#if [[ ! `crontab -l` == *"${update_script}"* ]]; then
#    crontab -l | { echo "*/1 * * * * PATH=$PATH:/usr/bin/env MAILTO=\"\" \"${update_script}\" 2>&1 | tee -a \"/var/log/${crontab_name}.log\" \n"; } | crontab -
#fi

