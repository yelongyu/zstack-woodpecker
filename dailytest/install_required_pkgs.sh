#!/bin/bash
#check and install some required tools for woodpecker testing.
which pip >&/dev/null
if [ $? -ne 0 ]; then
    echo "Need to install pip:"
    yum install -y python-pip 
    if [ $? -ne 0 ]; then
        echo "failed to install python-pip" && exit 1
    fi
fi
which ansible-playbook >&/dev/null
if [ $? -ne 0 ]; then
    echo "Need to install ansible:"
    yum install -y ansible
    if [ $? -ne 0 ]; then
        echo "failed to install ansible" && exit 1
    fi
fi
