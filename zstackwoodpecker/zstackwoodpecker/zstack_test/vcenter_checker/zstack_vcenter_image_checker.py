try:
    from pysphere import VIServer, MORTypes
except:
    print 'pysphere not installed'

import os
import sys
import traceback

import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.header.image as image_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.http as http
import zstacklib.utils.jsonobject as jsonobject
import zstacktestagent.plugins.vm as vm_plugin
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent
import apibinding.inventory as inventory
import zstacklib.utils.ssh as ssh


vcenter_ip = "172.20.76.251" 
sync_image_name = "MicroCore-Linux.ova"
domain_name = "administrator@vsphere.local"
password    = "Testing%123"

vm = None

class zstack_vcenter_image_file_checker(checker_header.TestChecker):
    '''check vcenter image file existence. If it is in backup storage, 
        return self.judge(True). If not, return self.judge(False)'''

    def check(self):
        super(zstack_vcenter_image_file_checker, self).check()

        server = VIServer()
        server.connect(vcenter_ip, domain_name, password)
        all_vms = server._get_managed_objects(MORTypes.VirtualMachine)

        for mor, name in all_vms.iteritems():
            if name == sync_image_name:
                return self.judge(True)
        else:        
            return self.judge(False)

        #cmd="sshpass -p password ssh root@ip \"ls /vmfs/volumes/datastore1/MicroCore-Linux.ova\""
        #ret, output, stderr = ssh.execute(cmd, vm.get_vm().vmNics[0].ip, "root", "password", False, 22)
        #if ret != 0:
        #    test_util.test_fail("generate 5GB big file failed")

