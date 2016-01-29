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

which vconfig  >&/dev/null
if [ $? -ne 0 ]; then
    echo "Need to install vconfig:"
    yum install -y vconfig
fi

which virtualenv >& /dev/null
[ $? -ne 0 ] && pip install virtualenv==12.1.1

which autoconf >& /dev/null
if [ $? -ne 0 ]; then
    echo "Need to install autoconf:"
    yum install -y autoconf
    if [ $? -ne 0 ]; then
        echo "failed to install autoconf" && exit 1
    fi
fi

which gcc >& /dev/null
if [ $? -ne 0 ]; then
    echo "Need to install gcc:"
    yum install -y gcc
    if [ $? -ne 0 ]; then
        echo "failed to install gcc" && exit 1
    fi
fi

rpm -q python-devel >&/dev/null
if [ $? -ne 0 ]; then
    echo "Need to install python-devel:"
    yum install python-devel
    if [ $? -ne 0 ]; then
        echo "failed to install python-devel" && exit 1
    fi
fi
