#!/bin/bash

ZSTACK_PYPI_URL=${ZSTACK_PYPI_URL-'https://pypi.python.org/simple/'}

help(){
    echo "Install woodpecker virtual environment. Need 2 parameters: 
    [the path of zstacklib.tar.gz]
    [the path of apibinding.tar.gz]
 
 For example: $0 /usr/local/zstack/zstacklib-0.1.0.tar.gz /usr/local/zstack/apibinding-0.1.0.tar.gz 
    
    If not providing 2 file paths, will only install zstacktestagent and 
    zstack-woodpecker. It might be failed, if 2 libs are not pre-installed"
    exit
}

if [ $# -eq 2 ]; then
    virtualenv_folder="/var/lib/zstack/virtualenv/woodpecker"
    virtualenv_file="${virtualenv_folder}/bin/activate"
    if [ ! -f $virtualenv_file ];then
        pip install virtualenv
        virtualenv $virtualenv_folder
    fi
    
    source $virtualenv_file
    pip install --ignore-installed -i $ZSTACK_PYPI_URL $1
    [ $? -ne 0 ] && echo "install $1 failed" && exit 1
    pip install --ignore-installed -i $ZSTACK_PYPI_URL $2
    [ $? -ne 0 ] && echo "install $2 failed" && exit 1
elif [ $# -ne 0 ]; then
    help
fi

dir_name=`dirname $0`
bash ${dir_name}/../zstacktestagent/install.sh
[ $? -ne 0 ] && echo "install testagent failed" && exit 1
bash ${dir_name}/../zstackwoodpecker/install.sh
[ $? -ne 0 ] && echo "install woodpecker failed" && exit 1

