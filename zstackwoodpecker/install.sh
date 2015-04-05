#!/bin/sh
root_dir=`dirname $0`
cd $root_dir
#install zstacktestagent firstly
../zstacktestagent/install.sh

rm -rf build dist zstackwoodpecker.egg-info zstackwoodpecker-*dev/
python setup.py sdist

pip uninstall -y zstackwoodpecker
pip install dist/*.tar.gz 
cp zstack-woodpecker /bin/

[ -d /root/.zstackwoodpecker ] || mkdir -p /root/.zstackwoodpecker
cp -a ansible /root/.zstackwoodpecker
