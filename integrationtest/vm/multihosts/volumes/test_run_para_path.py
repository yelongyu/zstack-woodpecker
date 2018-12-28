#coding:utf-8
'''

Robot Test only includes Vm operations, Volume operations and Snapshot operations

Case will run 1 hour with fair strategy. 

@author: Youyk
'''
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.action_select as action_select
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.test_state as ts_header
import os
import time

#Will sent 4000s as timeout, since case need to run at least ~3700s
_config_ = {
        'timeout' : 4600,
        'noparallel' : False
        }

test_dict = test_state.TestStateDict()
TestAction = ts_header.TestAction

templateContent = '''
{
    "ZStackTemplateFormatVersion": "2018-06-18",
    "Description": "本示例将创建一个云盘，并将云盘加载到云主机上(基于本地存储), 创建示例前提环境：\n计算规格，镜像，云盘规格，私有网络，可用物理机",
    "Parameters": {
        "InstanceOfferingUuid": {
            "Type": "String",
            "Label": "计算规格",
            "Description": "The instance offering uuid"
        },
        "ImageUuid":{
            "Type": "String",
            "Label": "镜像",
            "Description": "The Image uuid for creating VmInstance, Please choose an image not iso"
        },
        "PrivateNetworkUuid":{
            "Type": "String",
            "Label": "私有网络",
            "Description" : "The private network uuid for creating VmInstance"
        },
        "DiskofferingUuid":{
            "Type": "String",
            "Label": "云盘规格",
            "Description":"镜像服务器Uuid"
        }
    },
    "Resources": {
        "VmInstance": {
            "Type": "ZStack::Resource::VmInstance",
            "Properties": {
                "name": "vm1",
                "instanceOfferingUuid": {"Ref":"InstanceOfferingUuid"},
                "imageUuid":{"Ref":"ImageUuid"},
                "l3NetworkUuids":[{"Ref":"PrivateNetworkUuid"}]
            }
        },
        "DataVolume": {
            "Type": "ZStack::Resource::DataVolume",
            "Properties": {
                "name": "volume1",
                "diskOfferingUuid":{"Ref":"DiskofferingUuid"}
            }
        },
        "AttachDataVolumeToVm": {
            "Type": "ZStack::Action::AttachDataVolumeToVm",
            "Properties": {
                "vmInstanceUuid": {"Fn::GetAtt":["VmInstance","uuid"]},
                "volumeUuid": {"Fn::GetAtt":["DataVolume","uuid"]}
            }
        }
    },
    "Outputs": {
        "VmInstance": {
            "Value": {
                "Ref": "VmInstance"
            }
        }
    }
}

'''

def test():

    test_util.test_dsc('''Will mainly doing random test for all kinds of snapshot operations. VM, Volume and Image operations will also be tested. If reach 1 hour successful running condition, testing will success and quit.  SG actions, and VIP actions are removed in this robot test.
        VM resources: a special Utility vm is required to do volume attach/detach operation. 
        ''')
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('type', '=', 'UserVm', cond)
    instance_offering_queried = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)  
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))


    public_l3 = test_lib.lib_get_l3_by_name(os.environ.get('l3PublicNetworkName'))

    vm_create_option = test_util.VmOption()
    #image has to use virtual router image, as it needs to do port checking
    vm_create_option.set_image_uuid(test_lib.lib_get_image_by_name(img_name=os.environ.get('imageName_net')).uuid)

    utility_vm_create_option = test_util.VmOption()
    image_uuid = test_lib.lib_get_image_by_name(img_name=os.environ.get('imageName_net')).uuid
    utility_vm_create_option.set_image_uuid(image_uuid)
    l3_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3VlanNetworkName1')).uuid
    utility_vm_create_option.set_l3_uuids([l3_uuid])

    utility_vm = test_lib.lib_create_vm(utility_vm_create_option)
    test_dict.add_utility_vm(utility_vm)
    if os.environ.get('ZSTACK_SIMULATOR') != "yes":
        utility_vm.check()
    parameter = '{"PrivateNetworkUuid":"%s","ImageUuid":"%s","InstanceOfferingUuid":"%s","DiskofferingUuid":"%s"}' % (public_l3.uuid, image_uuid, instance_offering_queried[0].uuid, disk_offering.uuid)
    constant_path_list = [[TestAction.stop_vm, "vm1"],[TestAction.start_vm, "vm1"], [TestAction.detach_volume, "volume1"], [TestAction.attach_volume, "vm1", "volume1"]]

    test_util.test_dsc('Constant Path Test Begin.')
    robot_test_obj = test_util.Robot_Test_Object()
    robot_test_obj.set_utility_vm(utility_vm)
    robot_test_obj.set_initial_formation(templateContent)
    robot_test_obj.set_initial_formation_parameters(parameter)
    robot_test_obj.set_constant_path_list(constant_path_list)

    test_lib.lib_robot_create_initial_formation(robot_test_obj)
    rounds = 1
    current_time = time.time()
    timeout_time = current_time + 3600
    while time.time() <= timeout_time:
        test_util.test_dsc('New round %s starts: random operation pickup.' % rounds)
        test_lib.lib_robot_constant_path_operation(robot_test_obj)
        test_util.test_dsc('===============Round %s finished. Begin status checking.================' % rounds)
        rounds += 1
        test_lib.lib_robot_status_check(test_dict)
        if not robot_test_obj.get_constant_path_list():
            test_util.test_dsc('Reach test pass exit criterial: Required path executed %s' % (constant_path_list))
            break

    test_lib.lib_robot_cleanup(test_dict)
    test_util.test_pass('Snapshots Robot Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_robot_cleanup(test_dict)
