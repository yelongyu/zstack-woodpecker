#!/bin/sh

help(){
    echo "
    Usage: $0 Options
    It will calculate the time costing for creating multiple VMs.
    ----------------------------
    Option1     zstest.py path
    Option2     Test Case for creating VM. It could be a NUM or string. It
                should be aligned with the output of 'zstest.py -l'
                
    Option3     Test Case for destroying VM. It could be a NUM or string. It
                should be aligned with the output of 'zstest.py -l'

    option4     Initial VM creation case number, default is 1 [optional]
    Option5     Max VM creation case number, default is 20 [optional]
    Option6     VM creation case number increasing steps, default is 1[optional]
"
    exit 0
}

Exit(){
    echo $*
    exit 1
}

[ $# -lt 3 ] && help
zstest=$1
[ -f $zstest ] || Exit 'not find zstest.py in $zstest'
vm_creation=$2 
vm_destroy=$3
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

result='VMs\tCreation\tAvgC\t\tDestroy\t\tAvgD\n'
split='-------------------------------------------------------------'
result=$result$split
echo -e $result

cur_vm=$start_vm

while [ $cur_vm -le $max_vm ]; do
    echo -en $cur_vm'\t'

    creation_time=`ZSTACK_TEST_NUM=1 $zstest -c $vm_creation -r $cur_vm -p $cur_vm 2>/dev/null|grep 'Total test time'|awk -F 'time:' '{print $2}'|awk '{print $2}'|awk -F '(' '{print $2}'|awk -F ')' '{print $1}'`
    creation_time=`echo "scale = 3; $creation_time/1" |bc`
    echo -en $creation_time'\t\t'
    avg_time=`echo "scale = 3; $creation_time/$cur_vm" | bc`
    echo -en $avg_time'\t\t'
    
    sleep 1

    destroy_time=`$zstest -c $vm_destroy 2>/dev/null|grep 'Total test time' |awk -F 'time:' '{print $2}'|awk '{print $2}'|awk -F '(' '{print $2}'|awk -F ')' '{print $1}'`
    destroy_time=`echo "scale = 3; $destroy_time/1" |bc`
    echo -en $destroy_time'\t\t'
    avg_time=`echo "scale = 3; $destroy_time/$cur_vm" | bc`
    echo -e $avg_time''
    cur_vm=`expr $cur_vm + $step`
done
