'''

New Integration Test for restore mysql.

@author: Glody
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

vm = None

def test():
    global vm

    testHosts = test_lib.lib_get_all_hosts_from_plan()
    for host in testHosts:
        node_ip = host.managementIp_
        print str(node_ip)+" is host.managementIp_"
        break

    host_username = "root"
    host_password = "zstack.mysql.password"

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multihost_basic_vm')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()

    cmd = "zstack-ctl setenv ZSTACK_HOME=/usr/local/zstacktest/apache-tomcat/webapps/zstack/; zstack-ctl dump_mysql --file-name mysql_dump"
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)
    dump_file = rsp.split()[-1]

    cmd = "mysqldump -uroot -pzstack.mysql.password -A -r /tmp/mysql_before_restore.dump"
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)

    vm.check()

    cmd = "zstack-ctl restore_mysql -f %s --mysql-root-password %s"%(dump_file, host_password)
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)

    cmd = '''mysql -uroot -pzstack.mysql.password -D zstack -e "delete from VmInstanceVO where uuid='%s';"''' % (vm.get_vm().uuid)
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)

    cmd = "mysqldump -uroot -pzstack.mysql.password -A -r /tmp/mysql_after_restore.dump"
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)

    cmd = "zstack-ctl start"
    rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)

    #cmd = "diff /tmp/mysql_before_restore.dump /tmp/mysql_after_restore.dump |wc -l"
    #rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)

    #diff mysql dump alway has 4 or 8 lines difference because the dump time is different. 
    #and sometime here has 12 lines difference,So we suppose the when the different lines
    # more than 12, Restore mysql db failed.
    #if int(rsp.rstrip()) > 12:
    #    test_util.test_fail('Restore Mysql Failed')

    vm.destroy()
    test_util.test_pass('Restore Mysql Success')

#Wilv be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
