#!/bin/sh

#If not provide target folder as the parameter 1, the default will be:
default_folder='/home/img'

if [ "$1" != "" ]; then
    target_folder=$1
else
    target_folder=$default_folder
fi

echo "image download target folder is $target_folder"

mkdir -p $target_folder
cd $target_folder

#vr centos image
if [ ! -f vr-centos.img ];then
    rm -f vr-centos.img.gz
    wget -O vr-centos.img.gz https://www.dropbox.com/s/dg3ia88vpx7hzmm/vr-centos.img.gz 
    [ $? -eq 0 ] && gunzip -c vr-centos.img.gz |cat > vr-centos.img && rm -f vr-centos.img.gz
    #TODO: check MD5
else
    echo "vr-centos.img is found, skip downloading."
fi

##fedora19 image
if [ ! -f fedora19.img ];then
    rm -f fedora19.img.gz
    wget -O fedora19.img.gz https://www.dropbox.com/s/ehhlym6qpv7fg22/fedora19_5g.img.gz
    gunzip -c fedora19.img.gz |cat > fedora19.img
    rm -f fedora19.img.gz
    #TODO: check MD5
fi

#centos 6.4 image
if [ ! -f centos6.4.img ];then
    rm -f centos64.img.gz
    wget -O centos64.img.gz https://www.dropbox.com/s/lcfc9npyyabbba8/centos64_4g.img.gz
    gunzip -c centos64.img.gz |cat > centos6.4.img
    rm -f centos64.img.gz
    #TODO: check MD5
fi

#ubuntu12.04 image
if [ ! -f ubuntu12.04.img ];then
    rm -f ubuntu1204.img.gz
    wget -O ubuntu1204.img.gz https://www.dropbox.com/s/5ucw7vbmnnuzxfn/ubuntu12.04_5g.img.gz
    gunzip -c ubuntu1204.img.gz |cat > ubuntu12.04.img
    rm -f ubuntu1204.img.gz
    #TODO: check MD5
fi

