#!/bin/sh
root_dir=`dirname $0`
cd $root_dir
rm -rf build dist zstacktestagent.egg-info

python setup.py sdist
pip uninstall -y zstacktestagent
pip install  dist/*.tar.gz
