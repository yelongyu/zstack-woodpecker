#!/bin/bash
help(){
    echo "Usage: $0 [Options]"
    echo "Copy all xml config files to ~/.zstackwoodpecker/ for generating user
 local config. It will override user's local setting!"
    echo "Options: 
    -h                      show this message and exit
    -d WOODPECKER_PATH      [Optional] specify the woodpecker folder path. The
                            default path is the parent folder of this script.
    -f                      Override existed config file. Default will not 
                            override. 
    -x                      only copy xml files. Default will copy both .xml
                            and .tmpt files."
    exit
}


local_config_folder='/root/.zstackwoodpecker'

current_folder=`dirname $0`/../

COPY_OPTS='-n'

OPTIND=1
while getopts "d:hfx" Option; do
    case $Option in
        d ) current_folder=$OPTARG;;
        f ) COPY_OPTS='-f';;
        x ) ONLY_XML='y';;
        * ) help;;
    esac
done
OPTIND=1

if [ ! -d $current_folder/integrationtest ]; then
    echo "$(tput setaf 1)
Did not find $current_folder/integrationtest. Please pass right zstackwoodpecker
path with -d option. $(tput sgr0)
"
    help
fi

mkdir -p $local_config_folder
config_files=`find $current_folder/integrationtest -name '*.xml'`
for config_file in $config_files;do
    config_folder=${local_config_folder}/integrationtest/`echo $config_file|awk -F 'integrationtest' '{print $2}' | xargs dirname`
    mkdir -p $config_folder
    /bin/cp $COPY_OPTS $config_file $config_folder
    echo "[copy] $config_file [to] $config_folder"
done

if [ -z $ONLY_XML ]; then 
    config_temp_files=`find $current_folder/integrationtest -name '*.tmpt'`
    for config_temp_file in $config_temp_files;do
        config_folder=${local_config_folder}/integrationtest/`echo $config_temp_file|awk -F 'integrationtest' '{print $2}' | xargs dirname`
        mkdir -p $config_folder
        /bin/cp $COPY_OPTS $config_temp_file $config_folder
        echo "[copy] $config_temp_file [to] $config_folder"
    done
fi

echo "$(tput bold) - Has completed create local test config file folder in ${local_config_folder}/integrationtest/ . You can edit the deploy.tmpt and deploy.xml to align with local configurations. $(tput sgr0)"
