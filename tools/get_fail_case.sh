#!/bin/bash
set -x
ci_target=$1
buildid=$2

nfs_dir=/nfs/dir-1/disk1/mirror
root_dir=${nfs_dir}/${ci_target}/${buildid}
cd $root_dir
find . | grep errlogs/ > fail_case.log
echo "{" > reproduce_case.py
for i in `cat fail_case.log`
do
	case_name=`basename $i | awk -F- '{print $NF}' | awk -F"_id" '{print $1}'`
	ts=`basename $i | awk -F. '{print $1}' | cut -b 2-`
	echo $ts | grep "test"
	if [ $? -eq 0 ];then
		testsuite=`echo $ts | sed 's/_test//g'`
	else
		testsuite=$ts
	fi
	sub_dir=`basename $i`
	sub_dir2=`echo $sub_dir | awk -F- '{print $1}' | awk -F0 '{print $NF}' | cut -b 2-`
	#sub_dir1=`echo ${sub_dir#*0_}`
	#sub_dir2=`echo ${sub_dir1%-*}`
	echo "sub_dir2 is : $sub_dir2"
	case_dir=`dirname $i`
	config_dir="$case_dir/../../../../"
	config_file=`cat ${config_dir}test_config`
	sceniro_file=`cat ${config_dir}scenario_config`
	echo " case_name is :$case_name"
	echo " dir_name is :$case_dir"
	echo " config_dir is :$config_dir"
	echo " config_file is :$config_file"
	echo " sceniro_file is :$sceniro_file"
	if [ ! $sub_dir2 ];then
		echo "'$case_name' : 'TestSuiteJob(\"$ci_target\", \"nightly\", \"qwer\", \"$testsuite\", \"$config_file\", \"2\", reproduce_case=\"${testsuite}/${case_name}.py\", buildid=\"$buildid\", woodpecker=\"latest\", user=\"pengtao.zhang\",scenarioconfig=\"$sceniro_file\")'," >> reproduce_case.py
	else
		echo "'$case_name' : 'TestSuiteJob(\"$ci_target\", \"nightly\", \"qwer\", \"$testsuite\", \"$config_file\", \"2\", reproduce_case=\"${testsuite}/${sub_dir2}/${case_name}.py\", buildid=\"$buildid\", woodpecker=\"latest\", user=\"pengtao.zhang\",scenarioconfig=\"$sceniro_file\")'," >> reproduce_case.py
	fi
done
echo "}" >> reproduce_case.py

sshpass -p password scp $root_dir/reproduce_case.py root@172.20.198.87:/home/jenkins/test_script
