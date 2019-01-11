import subprocess
import sys
import os
import random
import re

TEST_CONF="/root/testconfig"
cfg=""
FILE_BASED=True
def bash_roe(cmd, errorout=False, ret_code = 0, pipe_fail=False):

    p = subprocess.Popen('/bin/bash', stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    if pipe_fail:
        cmd = 'set -o pipefail; %s' % cmd
    o, e = p.communicate(cmd)
    r = p.returncode

    if r != ret_code and errorout:
        raise BashError('failed to execute bash[%s], return code: %s, stdout: %s, stderr: %s' % (cmd, r, o, e))
    if r == ret_code:
        e = None

    return r, o, e

def format_disk():
    
    _,o1,_ = bash_roe("fdisk -l | grep Disk | grep dev | grep -v vda | grep -v mapper | awk '{print $2}' | awk -F':' '{print $1}'")

    for k in o1.split():
        bash_roe("echo -ne 'n\np\n1\n\n\nw\nq\n' | fdisk %s && mkfs.xfs %s1" % (k, k))

def scan_disk():
    import time
    time.sleep(1)

    _,o1_tmp,_ = bash_roe("ls -l /dev/disk/by-uuid | grep -v vda | grep -v dm | grep -v total | awk '{print $11}' | awk -F'/' '{print $3}'")
    o1=map(lambda x:"/dev/"+x,o1_tmp.strip().split())

    o2 = []
    for k in o1_tmp.strip().split():
        _,o2_tmp,_ = bash_roe("lsblk -n -d -r -p --output NAME,SIZE | grep %s | awk '{print $2}'" % k.strip('1'))
        o2.append(o2_tmp.strip())

    _,o3_tmp,_ = bash_roe("ls -l /dev/disk/by-uuid/ |  grep -v vda | grep -v dm | grep -v total | awk '{print $9}'")
    o3=map(lambda x:"/dev/disk/by-uuid/"+x,o3_tmp.strip().split())

    #_,o1,_ = bash_roe("lsblk -I 252,8,253 -n -d -r -p --output NAME,SIZE|grep -v vda|awk '{print $1}'")
    #_,o2,_ = bash_roe("lsblk -I 252,8,253 -n -d -r -p --output NAME,SIZE|grep -v vda|awk '{print $2}'")
    #_,o3,_ = bash_roe("lsblk -I 8 -n -d -r -p --output NAME,WWN|grep -v vda|awk '{print $2}'")

    disklist=dict(zip(o1,o2))
    diskuuid=dict(zip(o1,o3))
    for i in diskuuid.keys():
        _,o,_=bash_roe("lsblk %s -n -r --output WWN" % i)
        if o.strip():
            diskuuid[i]="/dev/disk/by-id/wwn-"+o.strip()+"-part1"

    #o4=map(lambda x:"/dev/disk/by-id/wwn-"+x,o3.strip().split())
    #disklist=dict(zip(o1.strip().split(),o2.strip().split()))
    #diskuuid=dict(zip(o1.strip().split(),o4))

    for k in diskuuid.keys():
        disklist[diskuuid[k]]=disklist.pop(k)

    return disklist

def prepare_testconfig(disklist):
    cfg=""
    global TEST_CONF,FILE_BASED
    if not FILE_BASED:
        for i,(k,v) in enumerate(disklist.items()):
            cfg=cfg + """
sd=sd{INDEX},lun={SDX},openflags=o_direct,size={SIZE},threads=16
""".format(INDEX=i,SDX=k,SIZE=v) 
        cfg=cfg + """
wd=wd1,sd=sd*,xfersize=256k,rdpct=60
rd=run1,wd=wd*,iorate=max,elapsed=60,interval=10
"""
    else:
        for i,(k,v) in enumerate(disklist.items()):
            cfg=cfg + """
fsd=fsd{INDEX},anchor=/{SDX}/dir1,depth=1,width=2,files=5,size=1m #{PATH}#{SIZE}
""".format(INDEX=i,SDX=os.path.basename(k),PATH=k,SIZE=v)
        cfg=cfg + """
fwd=fwd1,fsd=fsd*,operation=write,xfersize=128k,fileio=sequential,fileselect=random,threads=8
rd=rd1,fwd=fwd1,fwdrate=max,format=yes,elapsed=10,interval=1
"""
    with open(TEST_CONF, 'w') as fd:
        fd.write(cfg.strip())

def generate(disklist):
    global TEST_CONF
    if not disklist:
        print "no disk attached, skip generating"
        return
    if not FILE_BASED:
    	r,o,e = bash_roe("/root/vdbench/vdbench -f %s -jn" % TEST_CONF)
    else:
    	r,o,e = bash_roe("/root/vdbench/vdbench -f %s" % TEST_CONF)

    if r != 0:
        raise Exception(e)
    if r == 0:
        print "generate successfully"
    return r,o,e

def validate(disklist):
    global TEST_CONF,FILE_BASED
    if not FILE_BASED:
        r,o,e = bash_roe("/root/vdbench/vdbench -f %s -jr" % TEST_CONF)
        if r != 0:
            raise Exception(e)
        if r == 0:
            print "validate successfully"
    else:
        if not disklist:
            print "All old disks have been removed,skip validation"
            return "False"
        for i in disklist.keys():
            _,o,_=bash_roe("ls -t /%s/| grep md5sum_%s | head -n 2" % ('/'+os.path.basename(i),os.path.basename(i)))
            result,_,_=bash_roe("diff /%s/%s /%s/%s" % ('/'+os.path.basename(i),o.strip().split()[0],'/'+os.path.basename(i),o.strip().split()[1]))
            #bash_roe("rm /%s/md5sum*" % os.path.basename(i))
            bash_roe("umount /%s" % os.path.basename(i))
            bash_roe("rm -fr /%s" % os.path.basename(i))
            if result != 0:
                print "validate failed on ",i
                return False
        print "validate successfully"

def check_disk_from_last_ops():
    global TEST_CONF
    if not os.path.isfile(TEST_CONF):
        return False
    if not FILE_BASED:
        _,disk,_ = bash_roe("awk -F ',' '{print $2}' %s | grep lun |awk -F '=' '{print $2}'" % TEST_CONF)
        _,size,_ = bash_roe("awk -F ',' '{print $4}' %s |grep size |awk -F '=' '{print $2}'" % TEST_CONF)
    else:
        _,disk,_ = bash_roe("grep anchor %s | awk -F '#' '{print $2}'" % TEST_CONF)
        _,size,_ = bash_roe("grep size %s | awk -F '#' '{print $3}'" % TEST_CONF)
    return dict(zip(disk.strip().split(),size.strip().split()))

def print_disk_diff():
    i=""
    j=""
    diff_add={}
    diff_remove={}
    diff_resize={}
    disklist_old=check_disk_from_last_ops()
    if not disklist_old:
        return diff_add,diff_remove
    disklist_new=scan_disk()
    if cmp(disklist_old, disklist_new) == 0:
        print "same disk"
        return diff_add,diff_remove
    diff_add = dict(i for i in disklist_new.items() if i not in disklist_old.items())
    diff_remove = dict(j for j in disklist_old.items() if j not in disklist_new.items())
    for k in diff_remove.keys():
        if k in diff_add.keys():
            diff_remove.pop(k)
            diff_resize[k]=diff_add.pop(k)
    for i in diff_add.keys():
        print "add:%s:%s" % (i,diff_add[i])
    for i in diff_remove.keys():
        print "remove:%s:%s" % (i,diff_remove[i])
    for i in diff_resize.keys():
        print "resize:%s:%s" % (i,diff_resize[i])
    return diff_add,diff_remove

def mkdir_disk(disklist):
    for i in disklist.keys():
        bash_roe("mkdir -p /%s" % os.path.basename(i))
        bash_roe("mount %s /%s" % (i,os.path.basename(i)))

def clear_disk(disklist):
    for i in disklist.keys():
        bash_roe("umount /%s" % os.path.basename(i))
        bash_roe("rm -fr /%s" % os.path.basename(i))

def md5sum(disklist,flag):
    def md5sum_per_disk(diskname):
        def all_file(args,dirname,filename):
            for file in filename:
                file_path=os.path.join(dirname,file)
                if os.path.isfile(file_path): 
                    r,o,e=bash_roe("md5sum %s >> /%s/md5sum_%s" % (file_path,args[0],args[1]))
        os.path.walk("/"+diskname+"/dir1",all_file,(diskname, diskname+'_'+flag))
    for i in disklist.keys():
        md5sum_per_disk(os.path.basename(i))

if __name__ == "__main__":
    format_disk()
    diff_add,diff_remove=print_disk_diff()
    disklist=check_disk_from_last_ops()
    random_str=''.join(random.sample('abcdefghijklmnopqrstuvwxyz',3))
    if not disklist:
        disklist=scan_disk()

        if len(sys.argv) == 2:
            for i in disklist.keys():
                print "disklist:%s:%s" % (i,disklist[i])
            sys.exit(0)
        prepare_testconfig(disklist)
        if FILE_BASED:
            mkdir_disk(disklist)
        generate(disklist)
        if FILE_BASED:
            md5sum(disklist,random_str)
            clear_disk(disklist)
    else:
        if len(sys.argv) == 2:
            sys.exit(0)
        if diff_remove:
           for key,value in diff_remove.items():
               bash_roe("sed -i '/%s/d' %s" % (value,TEST_CONF))
               disklist.pop(key)
        if FILE_BASED:
            mkdir_disk(disklist)
            md5sum(disklist,random_str)
        validate(disklist)
        disklist=scan_disk()
        prepare_testconfig(disklist)
        if FILE_BASED:
            mkdir_disk(disklist)
        generate(disklist)
        if FILE_BASED:
            random_str=''.join(random.sample('abcdefghijklmnopqrstuvwxyz',3))
            md5sum(disklist,random_str)
            clear_disk(disklist)
