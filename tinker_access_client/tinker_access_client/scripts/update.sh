#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]; then
  echo "sudo required, try \"sudo bash ${BASH_SOURCE} ${@}\""
  exit 1
fi

#Disable for now...
#NOTE: Auto-Update will only be attempted if a versioned form of the tinker-access-client is already installed
#pip_package_name="tinker-access-client"
#${pip_package_name} --version >/dev/null 2>/dev/null
#if [ $? -eq 0 ]; then
#    restart_required=`pip install --upgrade --no-cache-dir ${pip_package_name}`
#    if [[ ${restart_required} == *"Successfully installed ${pip_package_name}"* ]]; then
#        ${pip_package_name} restart
#    fi
#fi
