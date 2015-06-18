#!/bin/sh

result_file=/tmp/zstack_perf_result

help(){
    echo "
    Usage: $0 zstest.py_PATH START_CASE CLEANUP_CASE START_NUM END_NUM STEPS PARALLEL_THREADS 
    It will calculate the time costing for creating multiple VMs.

    In each vm creation round, it will only call 1 test case. The detailed
    VM creation number will be sent by setting environment variable: 
    ZSTACK_TEST_NUM . 
    ----------------------------
    Option1     zstest.py path
    Option2     Test Case for creating VM. It could be a NUM or string. It
                should be aligned with the output of 'zstest.py -l'
                
    Option3     Test Case for destroying VM. It could be a NUM or string. It
                should be aligned with the output of 'zstest.py -l'

    option4     Initial VM creation case number, default is 1 [optional]
    Option5     Max VM creation case number, default is 20 [optional]
    Option6     VM creation case number increasing steps, default is 1[optional]
    Option7     Max parallel VM creation number
"
    exit 0
}

Exit(){
    echo $*
    rm -f $tmp_result
    exit 1
}

zstest_fail(){
    cat $tmp_result
    Exit 'zstest.py meets failure, please check errors in previous message'
}

cancel(){
    Exit 'cancel by user'
}

trap cancel INT

[ $# -lt 3 ] && help
zstest=$1
[ -f $zstest ] || Exit 'not find zstest.py in $zstest'
res_creation=$2 
res_destroy=$3
if [ $# -gt 3 ]; then
    start_vm=$4
else
    start_vm=1
fi

if [ $# -gt 4 ]; then
    max_vm=$5
else
    max_vm=20
fi

if [ $# -gt 5 ]; then
    step=$6
else
    step=1
fi

if [ $# -gt 6 ]; then
    thread=$7
else
    thread=1000
fi

tmp_result=`mktemp`

create_case=`$zstest -l |grep "\[${res_creation}\]"|awk '{print $3}'`
destroy_case=`$zstest -l |grep "\[${res_destroy}\]"|awk '{print $3}'`

echo "========================================"
echo "Create Case: $create_case"
echo "Destroy Case: $destroy_case"
echo "Start Number: $start_vm"
echo "End Number: $max_vm"
echo "Step: $step"
echo "Concurrency: $thread"
echo "========================================"
echo "Test case log could be found at: `dirname $zstest`/config_xml/test-result/"
echo "Test result will be saved in $result_file\n"
echo "========================================"

result='\nRes\tCreation\tAvgC\tDestroy\t\tAvgD\tCrt_Rst\tDst_Rst\n'
split='-----------------------------------------------------------------------------'
result=$split$result$split
echo -e $result |tee $result_file

cur_vm=$start_vm

while [ $cur_vm -le $max_vm ]; do
    echo -en $cur_vm'\t'
    export ZSTACK_TEST_NUM=$cur_vm
    export ZSTACK_THREAD_THRESHOLD=$thread
    $zstest -c $res_creation -t 72000 >$tmp_result 2>&1
    [ $? -ne 0 ] && zstest_fail
    creation_time=`cat $tmp_result|grep 'Total test time'|awk -F 'time:' '{print $2}'|awk '{print $2}'|awk -F '(' '{print $2}'|awk -F ')' '{print $1}'`
    creation_time=`echo "scale = 3; $creation_time/1" |bc`
    [ -z $creation_time ] && zstest_fail
    ct_size=${#creation_time}
    if [ $ct_size -ge 8 ]; then
        ct_string=$creation_time'\t'
    else
        ct_string=$creation_time'\t\t'
    fi

    c_pass_cases=`cat $tmp_result|grep 'Total:'|awk '{print $3}'`
    c_total_cases=`cat $tmp_result|grep 'Total:'|awk '{print $2}'`

    echo -en $ct_string|tee -a $result_file
    avg_time=`echo "scale = 3; $creation_time/$cur_vm" | bc`
    echo -en $avg_time'\t'|tee -a $result_file
    
    sleep 1

    $zstest -c $res_destroy -t 7200 >$tmp_result 2>&1
    [ $? -ne 0 ] && zstest_fail
    destroy_time=`cat $tmp_result |grep 'Total test time'|awk -F 'time:' '{print $2}'|awk '{print $2}'|awk -F '(' '{print $2}'|awk -F ')' '{print $1}'`
    destroy_time=`echo "scale = 3; $destroy_time/1" |bc`
    [ -z $destroy_time ] && zstest_fail
    echo -en $destroy_time'\t\t'|tee -a $result_file
    avg_time=`echo "scale = 3; $destroy_time/$cur_vm" | bc`
    d_pass_cases=`cat $tmp_result|grep 'Total:'|awk '{print $3}'`
    d_total_cases=`cat $tmp_result|grep 'Total:'|awk '{print $2}'`
    echo -en $avg_time'\t'|tee -a $result_file
    echo -en "$c_pass_cases/$c_total_cases"'\t'|tee -a $result_file
    echo -e "$d_pass_cases/$d_total_cases"|tee -a $result_file
    cur_vm=`expr $cur_vm + $step`
done

rm -f $tmp_result
