#!/bin/sh
root_dir=`dirname $0`
cd $root_dir
rm -rf build dist zstacktestagent.egg-info zstacktestagent-0.1.0

python setup.py sdist
pip uninstall -y zstacktestagent
pip install  dist/*.tar.gz
