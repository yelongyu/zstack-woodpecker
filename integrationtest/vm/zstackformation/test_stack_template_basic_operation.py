#coding:utf-8
'''

New Integration Test for creating KVM VM.

@author: Lei Liu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.stack_template as stack_template_ops
import zstackwoodpecker.operations.resource_operations as res_ops

def test():
    test_util.test_dsc("Test Stack template Apis")
    
    stack_template_option = test_util.StackTemplateOption()
    stack_template_option.set_name("test")
    templateContent = '''
{
    "ZStackTemplateFormatVersion": "2018-06-18",
    "Description": "《西游记》查看《西游记》书评和最新更新以及相关书籍推荐请到《西游记》专题网>址http://www.56wen.com
五六文学网 http://www.56wen.com，最有文学网站，提供经典的文学名著、武'小说、言小说、人文'社科类
书籍在线阅读，所有TXT电子书手机免费下载阅读，我们提供给您'的小说不求最多，但求最经典最完整
《》目录 第一回　灵根育孕源流出　心性修持大道生
诗曰：
混沌未分天地乱，茫茫渺渺无人见。
自从盘古破鸿蒙，开辟从兹清浊辨。
覆载群生仰至仁，发明万物皆成善。
欲知造化会元功，须看西游释厄传。
盖闻天地之数，有万元。将一元分为十二会，乃子、丑、寅、卯、辰、''、午、未、申、酉、戌、亥之十二>支也。每会该一万八百岁。>且就一日而论：子时阳气，而鸣；寅不通光，而卯则日出；辰时后，而排；日中
，而西蹉；申时晡而日落酉；戌黄昏而人定亥。譬于大>数，若到戌会之终，则否矣。再去五千四百岁，交初
，则当黑暗，而，故曰混沌。又五千四百岁，亥会将终，贞下起元，近子之会，而>复逐渐开明。邵康节曰：
“冬至子之半，天贺洲，曰洲，曰北俱芦洲。这洲。海外有一国土，名曰傲来国。国近大海，海中有一座山，
唤
为花果山。此山乃十洲之祖脉，三岛之来龙，自立，鸿而成。真山！有词赋为证。赋曰",
    "Parameters": {
        "TestStringBasicEcho": {
             "Type": "String",
             "Description":"最少八个最多十个字符，至少一个大写字母，一个小写字母，一
个数字和   殊",
             "Lable":"测试字符串",
             "DefaultValue":"testonly",
             "NoEcho":false
        },
        "TestStringChineseNoEcho": {
             "Type": "String",
             "Description":"最少八个最多十个字符，至少一个大写字母，一个小写字母，一
个数字和 殊",
             "Lable":"测试字符串",
             "DefaultValue":"testonly",
             "NoEcho":true
        },
        "TestStringSpecharsNoEcho": {
             "Type": "String",
             "Lable":"测试字符串",
             "NoEcho":true
        },
        "TestStringNullEcho": {
             "Type": "String"
        },
        "TestStringNullEcho": {
             "Type": "String",
             "NoEcho":true
        },
        "TestStringNULLEcho": {
             "Type": "String",
             "NoEcho":false
        },
        "TestNumberZeroNoEcho": {
             "Type": "Number",
             "DefaultValue": 0,
             "Description":"测试基本的数字0",
             "Lable":"测试数字",
             "NoEcho":true
        },
        "TestNumberNegativeEcho": {
             "Type": "Number",
             "Lable":"测试数字",
             "NoEcho":false
        },
        "TestNumberMaxEcho": {
             "Type": "Number",
             "Lable":"测试数字",
             "NoEcho":false
        },
        "TestNumberMinNoEcho": {
             "Type": "Number",
             "Lable":"测试数字",
             "NoEcho": true
        },
        "TestCommaDelimitedListNoEcho": {
            "Type": "CommaDelimitedList",
            "Description":"comma delimited list",
            "Lable":"测试CommaDelimitedList",
            "DefaultValue": "-1.123456789,1,2147483648,0.00, 0, 0.1, test",
            "NoEcho":true
        },
        "TestCommaDelimitedListEcho": {
            "Type": "CommaDelimitedList",
            "Description":"comma delimited list",
            "Lable":"测试CommaDelimitedList",
            "DefaultValue": "-1.123456789,1,2147483648,0.00, 0, 0.1, test"
        },
        "TestBooleanNoEcho": {
            "Type": "Boolean",
            "Description":"测试boolean ",
            "Lable":"测试Bool指",
            "DefaultValue": true,
            "NoEcho":true
        },
        "TestBooleanEcho": {
            "Type": "Boolean",
            "Description":"测试boolean ",
            "Lable":"测试Bool指",
            "DefaultValue": true
        },
        "TestJsonNoEcho": {
            "Type": "Json",
            "Description":"测试 Json",
            "NoEcho":true
        },
        "TestJsonEcho": {
            "Type": "Json",
            "Description":"测试 Json",
             "DefaultValue": {"menu": {
                          "id": "file",
                          "value": "File",
                          "popup": {
                            "menuitem": [
                              {"value": "New", "onclick": "CreateNewDoc()"},
                              {"value": "Open", "onclick": "OpenDoc()"},
                              {"value": "Close", "onclick": "CloseDoc()"}
                            ]
                          }
                        }}
                }
        },
    "Resources": {
        "InstanceOffering": {
            "Type": "ZStack::Resource::InstanceOffering",
            "Properties": {
                "name": "8cpu-8g",
                "cpuNum": 8,
                "memorySize": {"Ref":"TestNumberMaxEcho"}
            }
        }
    },
    "Outputs": {
        "InstanceOffering": {
            "Value": {
                "Ref": "InstanceOffering"
            }
        }
    }
}
'''
    stack_template_option.set_templateContent(templateContent)


    stack_template = stack_template_ops.add_stack_template(stack_template_option)

    cond = res_ops.gen_query_conditions('uuid', '=', stack_template.uuid)
    stack_template_queried = res_ops.query_resource(res_ops.STACK_TEMPLATE, cond)
    if len(stack_template_queried) == 0:
        test_util.test_fail("Fail to query stack template")
    #Add a template via text.

    newTemplateContent = '''
{
    "ZStackTemplateFormatVersion": "2018-06-18",
    "Description":"test",
    "Parameters": {
            "TestJsonEcho": {
            "Type": "Json",
            "Description":"测试 Json",
             "DefaultValue": {"menu": {
                          "id": "file",
                          "value": "File",
                          "popup": {
                            "menuitem": [
                              {"value": "New", "onclick": "CreateNewDoc()"},
                              {"value": "Open", "onclick": "OpenDoc()"},
                              {"value": "Close", "onclick": "CloseDoc()"}
                            ]
                          }
                        }}
                }
        },
    "Resources": {
        "InstanceOffering": {
            "Type": "ZStack::Resource::InstanceOffering",
            "Properties": {
                "name": "8cpu-8g",
                "cpuNum": 8,
                "memorySize": {"Ref":"TestNumberMaxEcho"}
            }
        }
    },
    "Outputs": {
        "InstanceOffering": {
            "Value": {
                "Ref": "InstanceOffering"
            }
        }
    }
}
'''

    stack_template_option.set_templateContent(newTemplateContent)
    stack_template_option.set_name("newname")

    new_stack_template = stack_template_ops.update_stack_template(stack_template.uuid, stack_template_option)

    if new_stack_template.name != "newname":
        test_util.test_fail("Fail to update stack template name")
    
    stack_template_ops.delete_stack_template(stack_template.uuid)

    stack_template_queried = res_ops.query_resource(res_ops.STACK_TEMPLATE, cond)
    if len(stack_template_queried) != 0:
        test_util.test_fail("Fail to query stack template")

    test_util.test_pass('Create Stack Template Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"
