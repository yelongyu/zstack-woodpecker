#coding:utf-8
def template():
    return '''
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

