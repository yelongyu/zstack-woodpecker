#!/bin/sh
woodpecker_virtualenv="/var/lib/zstack/virtualenv/woodpecker"
virtualenv_file="${woodpecker_virtualenv}/bin/activate"
if [ ! -f $virtualenv_file ];then
    echo "Not find virutalenv in /var/lib/zstack/virtualenv/woodpecker/. It should be created by virtualenv and install apibinding and zstacklib firstly. The easiest way is to run \`install_woodpecker_env.sh zstacklib.tar.gz apibinding.tar.gz\` or \`./zstest.py -b\`"
    exit 1
fi
source $virtualenv_file
root_dir=`dirname $0`
cd $root_dir
#install zstacktestagent firstly
../zstacktestagent/install.sh

rm -rf build dist zstackwoodpecker.egg-info zstackwoodpecker-*dev*/
python setup.py sdist

#pip uninstall -y zstackwoodpecker
rm -rf $woodpecker_virtualenv/usr/lib/python*/site-packages/zstackwoodpecker*
pip install dist/*.tar.gz 
cp zstack-woodpecker /bin/

[ -d /root/.zstackwoodpecker ] || mkdir -p /root/.zstackwoodpecker
cp -a ansible /root/.zstackwoodpecker
