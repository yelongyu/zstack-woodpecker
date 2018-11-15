#!/usr/bin/env python

import os
import sys
import re
import json
import threading
import time

PREFIX_NAME='vm_name'
NUM='number of vms'
#RANGE=NUM + 1
RANGE=NUM
vm_uuid=[]
MN_IP='vm_ip'
time_interval=300

def destroy_vm(session, vmuuid, host_ip):
    os.system('curl -s -H "Content-Type: application/json" -H "Authorization: OAuth'+session+'" -X DELETE http://'+host_ip+':8080/zstack/v1/vm-instances/'+vmuuid+'?deleteMode=Permissive')
    #os.system('zstack-cli DestroyVmInstance uuid=' + vmuuid)

def expunge_vm(session, vmuuid, host_ip):
    #os.system('curl -s -H "Content-Type: application/json" -H "Authorization: OAuth'+session+'" -X DELETE http://'+host_ip+':8080/zstack/v1/vm-instances/'+vmuuid+'?deleteMode=Permissive')
    os.system('curl -s -H "Content-Type: application/json" -H "Authorization: OAuth '+session+'" -X PUT -d \'{"expungeVmInstance":{}}\' http://'+host_ip+':8080/zstack/v1/vm-instances/'+vmuuid+'/actions')

os.system('zstack-cli -H '+MN_IP+' LogInByAccount accountName=admin password=password')

#for i in range(0, RANGE):
#    a = os.popen('zstack-cli -H '+MN_IP+' QueryVmInstance name='+PREFIX_NAME+'-'+str(i)).read()
#    dump = json.loads(a)
#    vm_uuid.append(dump['inventories'][0]['uuid'])

a = os.popen('zstack-cli -H '+MN_IP+' QueryVmInstance').read()
dump = json.loads(a)

for i in range(0, RANGE):
    for k in dump['inventories']:
        if k['name'] == PREFIX_NAME+'-'+str(i) :
            vm_uuid.append(k['uuid'])

output = os.popen('curl -s -H "Content-Type: application/json" -X PUT -d \'{"logInByAccount":{"accountName":"admin","password":"b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86"}}\' http://'+MN_IP+':8080/zstack/v1/accounts/login').read()
session = json.loads(output)['inventory']['uuid']

time.sleep(10)
#print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#os.system('ssh '+MN_IP+' date')

for i in range(0, NUM):
    thread = threading.Thread(target=destroy_vm, args=(session, vm_uuid[i], MN_IP))
    thread.start()

time.sleep(time_interval)

for i in range(0, NUM):
    thread = threading.Thread(target=expunge_vm, args=(session, vm_uuid[i], MN_IP))
    thread.start()
