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
    def _format_disk(disk=None):
        if disk:
            bash_roe("echo -ne 'n\np\n1\n\n\nw\nq\n' | fdisk %s && mkfs.xfs -f %s1" % (disk, disk))
            print "czhou:mkfs"
        else:
            _,o1,_ = bash_roe("fdisk -l | grep Disk | grep dev | grep -v vda | grep -v mapper | awk '{print $2}' | awk -F':' '{print $1}'")
    
            for k in o1.split():
                bash_roe("echo -ne 'n\np\n1\n\n\nw\nq\n' | fdisk %s && mkfs.xfs %s1" % (k, k))

    #_,o,_ = bash_roe("lsblk -I 252,8,253 -n -d -r -p --output NAME,SIZE|grep -v vda")
    _,tmp,_ = bash_roe("ls -l /dev/disk/by-uuid/ | grep -v vda | grep -v total | awk -F '/' '{print $3}'")
    _format_disk()
    if tmp:
        for k in tmp.split():
            bash_roe("mount /dev/%s /mnt" % k)
            if os.path.exists("/mnt/dir1"):
                bash_roe("umount /mnt")
                continue
            else:
                bash_roe("umount /mnt")
                _format_disk(disk="/dev/"+k.strip("1"))
            
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
        r,o,e=bash_roe("umount /%s" % os.path.basename(i))
        if r != 0:
            print "czhou:umount",e
        bash_roe("rm -fr /%s" % os.path.basename(i))

def md5sum(disklist,flag):
    md5sum_list = {}
    def md5sum_per_disk(disk_path):
        def all_file(args,dirname,filename):
            for file in filename:
                file_path=os.path.join(dirname,file)
                if os.path.isfile(file_path): 
                    r,o,e=bash_roe("md5sum %s >> /%s/md5sum_%s" % (file_path,args[0],args[1]))
        diskname = os.path.basename(disk_path)
        os.path.walk("/"+diskname+"/dir1",all_file,(diskname, diskname+'_'+flag))
        _,md,e = bash_roe("md5sum /%s/md5sum_%s | awk '{print $1}'" % (diskname, diskname+'_'+flag))
        md5sum_list[disk_path] = md.strip()
    for i in disklist.keys():
        md5sum_per_disk(i)
    return md5sum_list

def print_disklist(prefix, disklist, md5list=None):
    for i in disklist.keys():
        if md5list:
            print "%s disks:%s:%s:%s" % (prefix,i,disklist[i],md5list[i])
        else:
            print "%s disks:%s:%s" % (prefix,i,disklist[i])

def collect_md5sum(disklist):
    md5sum_list = {}
    mkdir_disk(disklist)
    for i in disklist.keys():
        _,o,_ = bash_roe("ls -t /%s/| grep md5sum_%s | head -n 1" % ('/'+os.path.basename(i),os.path.basename(i)))
        b,md5,a = bash_roe("md5sum /%s/%s | awk '{print $1}'" % (os.path.basename(i),o.strip())) 
        md5sum_list[i] = md5.strip()
    clear_disk(disklist)
    return md5sum_list

def print_dir(disklist):
    directory = {}
    for i in disklist.keys():
        _,o,_=bash_roe("ls -t /%s/| grep md5sum" % ('/'+os.path.basename(i)))
        directory[i] = o.strip()
    return directory

if __name__ == "__main__":
    format_disk() 
    random_str=''.join(random.sample('abcdefghijklmnopqrstuvwxyz',3))
    disklist=scan_disk()
    old_md5_list = collect_md5sum(disklist)
    print_disklist("old", disklist, old_md5_list)
    prepare_testconfig(disklist)
    if FILE_BASED:
        mkdir_disk(disklist)
    generate(disklist)
    if FILE_BASED:
        new_md5_list = md5sum(disklist,random_str)
        directory = print_dir(disklist)
        print_disklist("new", disklist, new_md5_list)
        print_disklist("directory", disklist, directory)
        clear_disk(disklist)
