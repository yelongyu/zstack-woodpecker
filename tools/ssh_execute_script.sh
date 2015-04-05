#!/bin/bash
# ssh target machine to do special scripts, which is under tools/ folder.
# The script will firstly scp the script to target machine's /tmp/ folder.
# Then it will ssh to the target machine and execute the copied script. 

# !!! To be noticed !!!: this script is a common script. After creating a local 
# executed script, e.g. local_script.sh, it is only to create a new soft link 
# from this script: ln -s ssh_execute_script.sh ssh_local_script.sh. When
# execute ssh_local_script.sh, it will automatically copy and execute the right
# script. 

# Author: yyk

if [ $# -eq 0 ]; then
    echo Not provide target machine. The Usage is \#$0 TARGET_MACHINE
    exit 1
fi

tools_path=`dirname $0`
script_file=`echo $0|awk -F 'ssh_' '{print $2}'`
source_script=${tools_path}/${script_file}
target_script=/tmp/${script_file}

if [ ! -f $source_script ];then
    echo not find $source_script
    exit 1
fi

echo $source_script

echo -e "$(tput bold) - scp script:$source_script to $1 $(tput sgr0)"
scp $source_script $1:/tmp/

if [ $? -ne 0 ]; then
    echo -e "$(tput setaf 1)\t: scp script:$source_script to $1 failed $(tput sgr0)"
    exit 1
fi

echo -e "$(tput bold) - ssh $1 to execute script:${target_script} $(tput sgr0)"
ssh $1 "sh ${target_script}"

if [ $? -ne 0 ]; then
    echo -e "$(tput setaf 1)\t: ssh execute script:${target_script} failed on $1$(tput sgr0)"
    exit 1
else
    echo -e "$(tput bold) - Successfully ssh to $1 to execute script:${target_script} $(tput sgr0)"
fi

