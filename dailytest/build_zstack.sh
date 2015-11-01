#!/bin/bash
# build ZStack binary 
ZSTACK_TEST_ROOT=${ZSTACK_TEST_ROOT-'/usr/local/zstack'}
PULL_ZSTACK="N"
PULL_ZSTACK_UTILITY="N"
PULL_ZSTACK_WOODPECKER="N"
PULL_ZSTACK_DASHBOARD="N"

help (){
    echo "Usage: $0 [options]

    Default option is -a
Options:
  -a            equal to -zuw
  -h            show this help message and exit
  -r            set zstack 'root' path, default is '/root'
  -u            pull zstack-utility
  -w            pull zstack-woodpecker
  -z            pull zstack 
"
    exit 1
}

PULL_FLAG='N'

OPTIND=1
while getopts "r:i:azuwh" Option
do
    case $Option in
        a ) PULL_ZSTACK='Y' && PULL_ZSTACK_UTILITY='Y' && PULL_ZSTACK_WOODPECKER='Y' && PULL_ZSTACK_DASHBOARD='Y'
            ;;
        z ) PULL_ZSTACK='Y' && PULL_FLAG='Y' ;;
        u ) PULL_ZSTACK_UTILITY=='Y' && PULL_FLAG='Y' ;;
        w ) PULL_ZSTACK_WOODPECKER='Y' && PULL_FLAG='Y' ;;
        r ) ZSTACK_TEST_ROOT=$OPTARG;;
        i) ;;
        h ) help;;
        * ) help;;
    esac
done
OPTIND=1
[ $PULL_FLAG == 'N' ] && PULL_ZSTACK='Y' && PULL_ZSTACK_UTILITY='Y' && PULL_ZSTACK_WOODPECKER='Y' && PULL_ZSTACK_DASHBOARD='Y'

ZSTACK_FOLDER=$ZSTACK_TEST_ROOT/zstack
ZSTACK_UTILITY=$ZSTACK_TEST_ROOT/zstack-utility
ZSTACK_WOODPECKER=$ZSTACK_TEST_ROOT/zstack-woodpecker
ZSTACK_DASHBOARD=$ZSTACK_TEST_ROOT/zstack-dashboard
ZSTACK_BUILD=$ZSTACK_UTILITY/zstackbuild
ZSTACK_ARCHIVE=$ZSTACK_TEST_ROOT/zstack_build_archive
#zstack_build_archive="install.sh zstack-all-in-one-*.tgz woodpecker/zstacktestagent.tar.bz  woodpecker/conf/zstack.properties"
zstack_build_archive="mevoco-installer*.bin woodpecker/zstacktestagent.tar.bz  woodpecker/conf/zstack.properties"
tab='  '

echo -e "\n - Build zstack.war and all test required packages. -"

echo_failure(){
    echo -e "$(tput setaf 1)${tab} ... ... $1\n$(tput sgr0)"
    exit 1
}

echo_pass(){
    echo -e "$(tput setaf 2)${tab} ... ... Success\n$(tput sgr0)"
}

install_pkg(){
    which $1 &>/dev/null
    if [ $? -ne 0 ];then 
        which yum &>/dev/null
        if [ $? -eq 0 ];then
            yum install -y $1
        else
            which apt-get && apt-get install -y $1
        fi
    fi
}

install_pkg git
install_pkg bzip2
install_pkg bc

if [ $PULL_ZSTACK == 'Y' ]; then
    echo -n "${tab} : Pull latest zstack"
    [ ! -d $ZSTACK_FOLDER ] && echo_failure "not find zstack repo folder:  $ZSTACK_FOLDER"
    cd $ZSTACK_FOLDER
    git pull >/dev/null

    if [ $? -ne 0 ]; then
        echo_failure "\'git pull\' failure in $ZSTACK_FOLDER"
    fi

    [ -d premium ] && cd premium && git pull >/dev/null
    echo_pass
else
    echo -e "${tab} : Skip pulling zstack\n"
fi

if [ $PULL_ZSTACK_WOODPECKER == 'Y' ]; then
    echo -n "${tab} : Pull latest zstack-woodpecker"
    [ ! -d $ZSTACK_WOODPECKER ] && echo_failure "not find zstack woodpecker repo folder:  $ZSTACK_WOODPECKER"
    cd $ZSTACK_WOODPECKER
    git pull >/dev/null
    if [ $? -ne 0 ]; then
        echo_failure "\'git pull\' failure in $ZSTACK_WOODPECKER"
    fi
    echo_pass
else
    echo -e "${tab} : Skip pulling zstack-woodpecker\n"
fi

if [ $PULL_ZSTACK_UTILITY == 'Y' ]; then
    echo -n "${tab} : Pull latest zstack-utility"
    [ ! -d $ZSTACK_UTILITY ] && echo_failure "not find zstack utility repo folder:  $ZSTACK_UTILTIY"
    cd $ZSTACK_UTILITY
    git pull >/dev/null
    if [ $? -ne 0 ]; then
        echo_failure "\'git pull\' failure in $ZSTACK_UTILITY"
    fi
    echo_pass
else
    echo -e "${tab} : Skip pulling zstack-utility\n"
fi

if [ $PULL_ZSTACK_DASHBOARD == 'Y' ]; then
    echo -n "${tab} : Pull latest zstack-dashboard"
    [ ! -d $ZSTACK_DASHBOARD ] && echo_failure "not find zstack dashboard repo folder:  $ZSTACK_DASHBOARD"
    cd $ZSTACK_DASHBOARD
    git pull >/dev/null
    if [ $? -ne 0 ]; then
        echo_failure "\'git pull\' failure in $ZSTACK_DASHBOARD"
    fi
    echo_pass
else
    echo -e "${tab} : Skip pulling zstack-dashboard\n"
fi

echo "${tab} : Build zstack all in one package"
cd $ZSTACK_BUILD
mkdir -p /tmp/zstack/

which ant

[ $? -ne 0 ] && which yum && yum install -y ant && yum install -y java-1.7.0-openjdk-devel && yum install -y maven

[ $? -ne 0 ] && which apt-get && apt-get install -y ant && apt-get install -y maven

#ant all-in-one -Dzstack_build_root=$ZSTACK_TEST_ROOT -Dbuild_name=qa -Dzstackdashboard.build_version=master|tee -a /tmp/zstack/build_log
ant -Dzstack_build_root=$ZSTACK_TEST_ROOT -Dzstackdashboard.build_version=master offline-centos7 |tee -a /tmp/zstack/build_log
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo_failure "build zstack failure"
    exit 1
fi
echo_pass

echo "${tab} : Build zstack test agent and test conf"
ant build-testconf -Dzstack_build_root=$ZSTACK_TEST_ROOT |tee -a /tmp/zstack/build_log
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo_failure "build zstack test conf"
    exit 1
fi

ant buildtestagent -Dzstack_build_root=$ZSTACK_TEST_ROOT |tee -a /tmp/zstack/build_log
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo_failure "build zstack test agent"
    exit 1
fi
echo_pass

mkdir -p ${ZSTACK_ARCHIVE}
zstack_archive_file=${ZSTACK_ARCHIVE}/zstack-all-in-one-`date +%y%m%d-%H%M`.tar
cd target
tar cf $zstack_archive_file $zstack_build_archive
rm -f ${ZSTACK_ARCHIVE}/latest
ln -s $zstack_archive_file ${ZSTACK_ARCHIVE}/latest
echo -e "$(tput setaf 2)\n - Build zstack successfully and saved as $zstack_archive_file - \n$(tput sgr0)"
