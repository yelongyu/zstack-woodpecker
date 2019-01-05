#coding:utf-8
'''

Robot Test run specified path 

@author: Quarkonics
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
                "l3NetworkUuids":[{"Ref":"PrivateNetworkUuid"}],
                "dataDiskOfferingUuids": [{"Ref":"DiskofferingUuid"},{"Ref":"DiskofferingUuid"},{"Ref":"DiskofferingUuid"},{"Ref":"DiskofferingUuid"},{"Ref":"DiskofferingUuid"},{"Ref":"DiskofferingUuid"},{"Ref":"DiskofferingUuid"},{"Ref":"DiskofferingUuid"}],
                "systemTags":[{"Fn::Join":["::",["virtio","diskOffering",{"Ref":"DiskofferingUuid"},"num","8"]]}]
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

templateContent2 = '''
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

templateContent3 = '''
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
                "l3NetworkUuids":[{"Ref":"PrivateNetworkUuid"}],
                "dataDiskOfferingUuids": [{"Ref":"DiskofferingUuid"}]
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

case_flavor = dict(path1=           dict(config=[{"ps1": "PS"}, {"ps1": "default"}], initial_formation=templateContent, path_list=[[TestAction.stop_vm, "vm1"], [TestAction.start_vm, "vm1"], [TestAction.delete_volume, "vm1-volume1"], [TestAction.create_image_from_volume, "vm1", "image1"], [TestAction.resize_volume, "vm1", 5*1024*1024], [TestAction.detach_volume, "vm1-volume2"], [TestAction.stop_vm, "vm1"], [TestAction.reinit_vm, "vm1"], [TestAction.start_vm, "vm1"], [TestAction.resize_volume, "vm1", 5*1024*1024], [TestAction.detach_volume, "vm1-volume3"], [TestAction.stop_vm, "vm1"], [TestAction.change_vm_image, "vm1"], [TestAction.create_data_vol_template_from_volume, "vm1-volume2", "image2"], [TestAction.reboot_vm, "vm1"]]),
                   path2=           dict(config=[{"ps1": "PS"}, {"ps1": "default"}], initial_formation=templateContent2, path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi"], [TestAction.create_data_volume_from_image, "volume2", "=scsi"], [TestAction.create_data_volume_from_image, "volume3", "=scsi"], [TestAction.create_data_volume_from_image, "volume4", "=scsi"], [TestAction.create_data_volume_from_image, "volume5", "=scsi"], [TestAction.create_data_volume_from_image, "volume6", "=scsi"], [TestAction.create_data_volume_from_image, "volume7", "=scsi"], [TestAction.create_data_volume_from_image, "volume8", "=scsi"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.attach_volume, "vm1", "volume3"], [TestAction.attach_volume, "vm1", "volume4"], [TestAction.attach_volume, "vm1", "volume5"], [TestAction.attach_volume, "vm1", "volume6"], [TestAction.attach_volume, "vm1", "volume7"], [TestAction.attach_volume, "vm1", "volume8"], [TestAction.detach_volume, "volume2"], [TestAction.migrate_vm, "vm1"], [TestAction.ps_migrate_volume, "volume2"], [TestAction.delete_volume, "volume2"], [TestAction.create_image_from_volume, "vm1", "image1"], [TestAction.create_volume_snapshot, "volume3", 'snapshot1'], [TestAction.detach_volume, "volume3"], [TestAction.cleanup_ps_cache], [TestAction.create_volume_snapshot, "volume3", 'snapshot2'], [TestAction.reboot_vm, "vm1"]]),
                   path3=           dict(config=[{"ps1": "PS"}, {"ps1": "default"}], initial_formation=templateContent2, path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi,shareable"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.reboot_vm, "vm1"], [TestAction.create_backup, "vm1-root", "backup1"], [TestAction.detach_volume, "volume1"], [TestAction.create_image_from_volume, "vm1", "image1"], [TestAction.create_data_vol_template_from_volume, "volume1", "image2"], [TestAction.delete_volume, "volume1"], [TestAction.clone_vm, "vm1"], [TestAction.create_data_volume_from_image, "volume2", "=scsi,shareable"], [TestAction.ps_migrate_volume, "volume2"], [TestAction.reboot_vm, "vm1"]]),
                   path4=           dict(config=[{"ps1": "PS"}, {"ps1": "default"}], initial_formation=templateContent3, path_list=[[TestAction.delete_volume, "vm1-volume1"], [TestAction.stop_vm, "vm1"], [TestAction.ps_migrate_volume, "vm1-root"], [TestAction.start_vm, "vm1"], [TestAction.create_volume, "volume2"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.detach_volume, "volume2"], [TestAction.create_volume_snapshot, "volume2", "snapshot1"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.create_volume_snapshot, "vm1-root", "snapshot2"], [TestAction.use_volume_snapshot, "snapshot1"], [TestAction.delete_volume, "volume2"], [TestAction.cleanup_ps_cache], [TestAction.use_volume_snapshot, "snapshot1"], [TestAction.reboot_vm, "vm1"]]),
                   path5=           dict(config=[{"ps1": "PS"}, {"ps1": "default"}], initial_formation=templateContent, path_list=[[TestAction.delete_volume, "vm1-volume1"], [TestAction.reinit_vm, "vm1"], [TestAction.create_data_vol_template_from_volume, "vm1-volume2", "image1"], [TestAction.delete_volume, "vm-volume2"], [TestAction.reboot_vm, "vm1"], [TestAction.create_backup, "vm1-volume3", "backup1"], [TestAction.detach_volume, "vm1-volume3"], [TestAction.reinit_vm, "vm1"], [TestAction.ps_migrate_volume, "vm1-volume3"], [TestAction.reboot_vm, "vm1"]]),
                   path6=           dict(config=[{"ps1": "PS"}, {"ps1": "default"}], initial_formation=templateContent2, path_list=[[TestAction.create_data_volume_from_image, "volume1", "=scsi,shareable"], [TestAction.create_data_volume_from_image, "volume2", "=scsi,shareable"], [TestAction.create_data_volume_from_image, "volume3", "=scsi,shareable"], [TestAction.create_data_volume_from_image, "volume4", "=scsi,shareable"], [TestAction.create_data_volume_from_image, "volume5", "=scsi,shareable"], [TestAction.create_data_volume_from_image, "volume6", "=scsi,shareable"], [TestAction.create_data_volume_from_image, "volume7", "=scsi,shareable"], [TestAction.create_data_volume_from_image, "volume8", "=scsi,shareable"], [TestAction.attach_volume, "vm1", "volume1"], [TestAction.attach_volume, "vm1", "volume2"], [TestAction.attach_volume, "vm1", "volume3"], [TestAction.attach_volume, "vm1", "volume4"], [TestAction.attach_volume, "vm1", "volume5"], [TestAction.attach_volume, "vm1", "volume6"], [TestAction.attach_volume, "vm1", "volume7"], [TestAction.attach_volume, "vm1", "volume8"], [TestAction.delete_volume, "volume2"], [TestAction.cleanup_ps_cache], [TestAction.detach_volume, "volume3"], [TestAction.ps_migrate_volume, "volume3"], [TestAction.create_volume, "volume9"], [TestAction.stop_vm, "vm1"], [TestAction.change_vm_image, "vm1"], [TestAction.start_vm, "vm1"], [TestAction.detach_volume, "volume4"], [TestAction.ps_migrate_volume, "volume4"], [TestAction.detach_volume, "volume5"], [TestAction.detach_volume, "volume6"], [TestAction.detach_volume, "volume7"], [TestAction.detach_volume, "volume8"], [TestAction.ps_migrate_volume, "vm1-root"], [TestAction.resize_volume, "volume5"], [TestAction.reboot_vm, "vm1"]]))

def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    initial_formation = flavor['initial_formation']
    config = flavor['config']
    path_list = flavor['path_list']

    test_util.test_dsc('''Will mainly doing random test for all kinds of snapshot operations. VM, Volume and Image operations will also be tested. If reach 1 hour successful running condition, testing will success and quit.  SG actions, and VIP actions are removed in this robot test.
        VM resources: a special Utility vm is required to do volume attach/detach operation. 
        ''')

    test_util.test_dsc('Constant Path Test Begin.')
    robot_test_obj = test_util.Robot_Test_Object()
    robot_test_obj.set_config(config)
    robot_test_obj.set_initial_formation(initial_formation)
    robot_test_obj.set_constant_path_list(path_list)

    test_lib.lib_robot_create_initial_formation(robot_test_obj)
    test_lib.lib_robot_create_utility_vm(robot_test_obj)
    rounds = 1
    current_time = time.time()
    timeout_time = current_time + 3600
    while time.time() <= timeout_time:
        test_util.test_dsc('New round %s starts:' % rounds)
        test_lib.lib_robot_constant_path_operation(robot_test_obj)
        test_util.test_dsc('===============Round %s finished. Begin status checking.================' % rounds)
        rounds += 1
        test_lib.lib_robot_status_check(test_dict)
        if not robot_test_obj.get_constant_path_list():
            test_util.test_dsc('Reach test pass exit criterial: Required path executed %s' % (path_list))
            break

    test_lib.lib_robot_cleanup(test_dict)
    test_util.test_pass('Snapshots Robot Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_robot_cleanup(test_dict)
