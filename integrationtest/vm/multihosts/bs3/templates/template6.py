#coding:utf-8
def template():
    return '''

{
    "ZStackTemplateFormatVersion": "2018-06-18",
    "Description": "本示例将添加一个镜像，然后用镜像创建云主机。",
    "Parameters": {
        "L3NetworkUuid":{
            "Type": "String",
            "Label": "三层网络"
        },
        "BackupStorageUuid":{
            "Type": "CommaDelimitedList",
            "Label": "镜像服务器"
        }
    },
    "Resources": {
        "VmInstance": {
            "Type": "ZStack::Resource::VmInstance",
            "Properties": {
                "name": "vm1",
                "instanceOfferingUuid": {"Fn::GetAtt":["InstanceOffering","uuid"]},
                "imageUuid":{"Fn::GetAtt":["Image","uuid"]},
                "l3NetworkUuids":[{"Ref":"L3NetworkUuid"}]
            }
        },
        "InstanceOffering": {
            "Type": "ZStack::Resource::InstanceOffering",
            "Properties": {
                "name":"1G-1CPU-STACK",
                "description":"测试创建计算规格",
                "cpuNum": 1,
                "memorySize": 1073741824
            }
        },
        "Image": {
            "Type": "ZStack::Resource::Image",
            "Properties": {
                "name": "image1",
                "backupStorageUuids": {"Ref":"BackupStorageUuid"},
                "url":"file:///opt/zstack-dvd/zstack-image-1.4.qcow2",
                "format": "qcow2"
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

