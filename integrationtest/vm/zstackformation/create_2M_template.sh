m=150
echo "{" >> large_template.json
echo "  \"ZStackTemplateFormatVersion\": \"2018-06-18\"," >> large_template.json
echo "  \"Description\": \"Test ZStack formation functions\"," >> large_template.json
echo "  \"Mappings\": { " >> large_template.json
echo "    \"names\": { " >> large_template.json
echo "      \"instanceOffering\": { " >> large_template.json
echo "        \"name1\": \"test-just-t\", " >> large_template.json
echo "        \"name2\": \"test2\" " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"JustForTest\": { " >> large_template.json
echo "      \"test\": \"I am valid!\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"JustForTest2\": { " >> large_template.json
echo "      \"test\": \"I am valid!\", " >> large_template.json
echo "      \"test2\": \"I am valid too!\" " >> large_template.json
echo "    } " >> large_template.json
echo "  }, " >> large_template.json
echo "  \"Parameters\": { " >> large_template.json

i=1
while true
do
echo "round $i parameters"
echo "    \"4TestBoolean2${i}\": { " >> large_template.json
echo "      \"Type\": \"Boolean\", " >> large_template.json
echo "      \"Description\": \"测试boolean \", " >> large_template.json
echo "      \"DefaultValue\": false " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"ZoneUuid${i}\": { " >> large_template.json
echo "      \"Type\": \"String\", " >> large_template.json
echo "      \"Description\": \"测试boolean \", " >> large_template.json
echo "      \"DefaultValue\": \"zoneuuid${i}\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"ClusterUuid${i}\": { " >> large_template.json
echo "      \"Type\": \"String\", " >> large_template.json
echo "      \"DefaultValue\": \"clusteruuid${i}\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"PrimaryStorageUuidForRootVolume${i}\": { " >> large_template.json
echo "      \"Type\": \"String\", " >> large_template.json
echo "      \"Description\": \"主存储Uuid \", " >> large_template.json
echo "      \"DefaultValue\": \"primarystorageuuidforrootvolume${i}\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"ImageUrl${i}\": { " >> large_template.json
echo "      \"Type\": \"String\", " >> large_template.json
echo "      \"Description\": \"镜像地址\", " >> large_template.json
echo "      \"DefaultValue\": \"http://test.zss.com/testimage${i}.qcow2\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"BackupStorages${i}\": { " >> large_template.json
echo "      \"Type\": \"CommaDelimitedList\", " >> large_template.json
echo "      \"Description\": \"所有镜像服务器\", " >> large_template.json
echo "      \"DefaultValue\": \"BS1,BS2,BS3\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"Vlan${i}\": { " >> large_template.json
echo "      \"Type\": \"Number\", " >> large_template.json
echo "      \"Description\": \"Vlan id\", " >> large_template.json
echo "      \"DefaultValue\": 1000${i} " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"VipPortStart${i}\": { " >> large_template.json
echo "      \"Type\": \"Number\", " >> large_template.json
echo "      \"Description\": \"Vip port start num\", " >> large_template.json
echo "      \"DefaultValue\": 22${i} " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"LoadBalancerPort${i}\": { " >> large_template.json
echo "      \"Type\": \"Number\", " >> large_template.json
echo "      \"Description\": \"load balancer port\", " >> large_template.json
echo "      \"DefaultValue\": 443${i} " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"PeerAddress${i}\": { " >> large_template.json
echo "      \"Type\": \"String\", " >> large_template.json
echo "      \"DefaultValue\": \"192.168.200.10${i}\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"AuthKey${i}\": { " >> large_template.json
echo "      \"Type\": \"String\", " >> large_template.json
echo "      \"DefaultValue\": \"testAuthKey${i}\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"L2Interface${i}\": { " >> large_template.json
echo "      \"Type\": \"String\", " >> large_template.json
echo "      \"DefaultValue\": \"eth${i}\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"StartIp${i}\":{ " >> large_template.json
echo "      \"Type\":\"String\", " >> large_template.json
echo "      \"DefaultValue\":\"192.168.200.${i}\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"EndIp${i}\":{ " >> large_template.json
echo "      \"Type\":\"String\", " >> large_template.json
echo "      \"DefaultValue\":\"192.168.200.2${i}\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"Netmask${i}\":{ " >> large_template.json
echo "      \"Type\":\"String\", " >> large_template.json
echo "      \"DefaultValue\":\"255.255.255.0\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"Gateway${i}\":{ " >> large_template.json
echo "      \"Type\":\"String\", " >> large_template.json
echo "      \"DefaultValue\":\"192.268.200.1\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"Dns${i}\":{ " >> large_template.json
echo "      \"Type\":\"String\", " >> large_template.json
echo "      \"DefaultValue\":\"114.114.114.114\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"NetworkCidr${i}\":{ " >> large_template.json
echo "      \"Type\":\"String\", " >> large_template.json
echo "      \"DefaultValue\":\"192.168.10.0/24\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"Destination${i}\":{ " >> large_template.json
echo "      \"Type\":\"String\", " >> large_template.json
echo "      \"DefaultValue\":\"192.168.2.0/24\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"Prefix${i}\":{ " >> large_template.json
echo "      \"Type\":\"String\", " >> large_template.json
echo "      \"DefaultValue\":\"169.254.169.254/32\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"Nexthop${i}\":{ " >> large_template.json
echo "      \"Type\":\"String\", " >> large_template.json
echo "      \"DefaultValue\":\"192.168.1.254\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"UsbDeviceUuid${i}\":{ " >> large_template.json
echo "      \"Type\":\"String\", " >> large_template.json
echo "      \"DefaultValue\":\"usbDeviceUuid${i}\" " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"PciDeviceUuid${i}\":{ " >> large_template.json
echo "      \"Type\":\"String\", " >> large_template.json
echo "      \"DefaultValue\":\"pciDeviceUuid${i}\" " >> large_template.json
echo "    }, " >> large_template.json
	let i=${i}+1
	
	if [ $i -eq $m ];then
	    break
	fi
done

echo "  }, " >> large_template.json
echo "  \"Resources\": { " >> large_template.json
i=1
while true
do
echo "round $i resource"
echo "    \"InstanceOffering${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::InstanceOffering\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": { " >> large_template.json
echo "          \"Fn::Join\": [ " >> large_template.json
echo "            \"-\", " >> large_template.json
echo "            [ " >> large_template.json
echo "              \"a\", " >> large_template.json
echo "              \"b\", " >> large_template.json
echo "              \"ccc\" " >> large_template.json
echo "            ] " >> large_template.json
echo "          ] " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"description\":\"测试创建计算规格\", " >> large_template.json
echo "        \"cpuNum\": 8, " >> large_template.json
echo "        \"memorySize\": 8589934592, " >> large_template.json
echo "        \"allocatorStrategy\":\"Mevoco\", " >> large_template.json
echo "        \"resourceUuid\":\"testuuid\", " >> large_template.json
echo "        \"sortKey\":0, " >> large_template.json
echo "        \"systemTags\": [ " >> large_template.json
echo "          \"userdata\" " >> large_template.json
echo "        ], " >> large_template.json
echo "        \"userTags\": [ " >> large_template.json
echo "          \"中文\", " >> large_template.json
echo "          \"testinstanceofferingusertag\" " >> large_template.json
echo "        ], " >> large_template.json
echo "        \"type\":\"UserVm\", " >> large_template.json
echo "        \"timeout\":600 " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"DiskOffering${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::DiskOffering\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"diskoffering${i}\", " >> large_template.json
echo "        \"diskSize\": 1124774006935781000, " >> large_template.json
echo "        \"sortKey\": 1, " >> large_template.json
echo "        \"allocationStrategy\": \"DefaultPrimaryStorageAllocationStrategy\", " >> large_template.json
echo "        \"resourceUuid\": \"DefaultDiskOfferingType\", " >> large_template.json
echo "        \"type\": \"DefaultDiskOfferingType\", " >> large_template.json
echo "        \"timeout\":100, " >> large_template.json
echo "        \"systemTags\": [ " >> large_template.json
echo "          \"test\", " >> large_template.json
echo "          \"ttt\" " >> large_template.json
echo "        ], " >> large_template.json
echo "        \"userTags\": [ " >> large_template.json
echo "          \"中文\", " >> large_template.json
echo "          \"testdiskofferingusertag\" " >> large_template.json
echo "        ] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"VM${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::VmInstance\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": { " >> large_template.json
echo "          \"Fn::Base64\": \"kubernetes-Node-1\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"instanceOfferingUuid\": { " >> large_template.json
echo "          \"Fn::GetAtt\": [ " >> large_template.json
echo "            \"InstanceOffering${i}\", " >> large_template.json
echo "            \"uuid\" " >> large_template.json
echo "          ] " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"imageUuid\": { " >> large_template.json
echo "          \"Fn::FindInMap\": [ " >> large_template.json
echo "            \"names\", " >> large_template.json
echo "            \"instanceOffering\", " >> large_template.json
echo "            \"name1\" " >> large_template.json
echo "          ] " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"l3NetworkUuids\": [\"1\",\"2\"], " >> large_template.json
echo "        \"rootDiskOfferingUuid\": { " >> large_template.json
echo "          \"Fn::GetAtt\": [ " >> large_template.json
echo "            \"DiskOffering${i}\", " >> large_template.json
echo "            \"uuid\" " >> large_template.json
echo "          ] " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"dataDiskOfferingUuids\": [ " >> large_template.json
echo "          \"uuid1\", " >> large_template.json
echo "          \"uuid2\" " >> large_template.json
echo "        ], " >> large_template.json
echo "        \"zoneUuid\": { " >> large_template.json
echo "          \"Ref\": \"ZoneUuid${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"clusterUuid\": { " >> large_template.json
echo "          \"Ref\": \"ClusterUuid${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"hostUuid\": \"hostuuid\", " >> large_template.json
echo "        \"primaryStorageUuidForRootVolume\": { " >> large_template.json
echo "          \"Ref\": \"PrimaryStorageUuidForRootVolume${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"description\": \"创建一个云主机··‘’“''、$# $?\", " >> large_template.json
echo "        \"defaultL3NetworkUuid\": \"uuid\", " >> large_template.json
echo "        \"strategy\":\"InstantStart\", " >> large_template.json
echo "        \"timeout\":300, " >> large_template.json
echo "        \"systemTags\": [ " >> large_template.json
echo "          \"userdata\" " >> large_template.json
echo "        ], " >> large_template.json
echo "        \"userTags\": [ " >> large_template.json
echo "          \"Test\", " >> large_template.json
echo "          \"test2\", " >> large_template.json
echo "          \"中文试一下;\" " >> large_template.json
echo "        ] " >> large_template.json
echo "      }, " >> large_template.json
echo "      \"DependsOn\": [ " >> large_template.json
echo "        { " >> large_template.json
echo "          \"Ref\": \"InstanceOffering${i}\" " >> large_template.json
echo "        } " >> large_template.json
echo "      ], " >> large_template.json
echo "      \"DeletionPolicy\": \"Retain\" " >> large_template.json
echo "    }, " >> large_template.json
echo "   \"DataVolume${i}\": { " >> large_template.json
echo "    \"Type\": \"ZStack::Resource::DataVolume\", " >> large_template.json
echo "    \"Properties\": { " >> large_template.json
echo "        \"name\": \"testDataVolume${i}\", " >> large_template.json
echo "        \"description\": \"创建一个云盘！！！\", " >> large_template.json
echo "        \"diskOfferingUuid\": { " >> large_template.json
echo "            \"Fn::GetAtt\": [ " >> large_template.json
echo "                \"DiskOffering${i}\", " >> large_template.json
echo "                \"uuid\" " >> large_template.json
echo "            ] " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"primaryStorageUuid\": { " >> large_template.json
echo "            \"Ref\": \"PrimaryStorageUuidForRootVolume${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"resourceUuid\": \"uuid\", " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\": [ " >> large_template.json
echo "            \"test\", " >> large_template.json
echo "            \"ttt\" " >> large_template.json
echo "        ], " >> large_template.json
echo "        \"userTags\": [ " >> large_template.json
echo "            \"Test\", " >> large_template.json
echo "            \"test2\", " >> large_template.json
echo "            \"中文试一下;\" " >> large_template.json
echo "        ] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"Image${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::Image\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testimage${i}\", " >> large_template.json
echo "        \"description\": \"添加镜像，‘’‘’“”\", " >> large_template.json
echo "        \"url\": { " >> large_template.json
echo "          \"Ref\": \"ImageUrl${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"mediaType\": \"ISO\", " >> large_template.json
echo "        \"guestOsType\": \"Linux\", " >> large_template.json
echo "        \"system\": false, " >> large_template.json
echo "        \"format\": \"qcow2\", " >> large_template.json
echo "        \"platform\": \"Linux\", " >> large_template.json
echo "        \"mediaType\": \"RootVolumeTemplate\", " >> large_template.json
echo "        \"backupStorageUuids\": { " >> large_template.json
echo "          \"Ref\": \"BackupStorages${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"resourceUuid\": \"testuuid\", " >> large_template.json
echo "        \"timeout\":600, " >> large_template.json
echo "        \"systemTags\": [ " >> large_template.json
echo "          \"imagesystemtags\", " >> large_template.json
echo "          \"imagestsytemtages2\" " >> large_template.json
echo "        ], " >> large_template.json
echo "        \"userTags\": [ " >> large_template.json
echo "          \"imageusertages1\", " >> large_template.json
echo "          \"imageusertages2\", " >> large_template.json
echo "          \"中文试一下\" " >> large_template.json
echo "        ] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"AffinityGroup${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::AffinityGroup\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testAffinityGroup${i}\", " >> large_template.json
echo "        \"description\":\"create one 亲和组 \", " >> large_template.json
echo "        \"policy\": \"antiSoft\", " >> large_template.json
echo "        \"type\": \"host\", " >> large_template.json
echo "        \"resourceUuid\": \"affinitygroupuuid\", " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\": [\"testsystemTags\"], " >> large_template.json
echo "        \"userTags\": [\"用户标签\"] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"L2VxlanNetworkPool${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::L2VxlanNetworkPool\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testl2vxlannetworkpool${i}\", " >> large_template.json
echo "        \"description\":\"一个vxlanpool\", " >> large_template.json
echo "        \"type\":\"test\", " >> large_template.json
echo "        \"zoneUuid\": { " >> large_template.json
echo "          \"Ref\": \"ZoneUuid${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"physicalInterface\": { " >> large_template.json
echo "          \"Ref\": \"L2Interface${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"timeout\":100, " >> large_template.json
echo "        \"resourceUuid\": \"testl2vxlannetworkpooluuid\", " >> large_template.json
echo "        \"systemTags\": [ " >> large_template.json
echo "          \"l2vxlanpoolsystemtags\", " >> large_template.json
echo "          \"l2vxlanpoolsystemtages2\" " >> large_template.json
echo "        ], " >> large_template.json
echo "        \"userTags\": [ " >> large_template.json
echo "          \"l2vxlanpoolsertages1\", " >> large_template.json
echo "          \"l2vxlanpoolertages2\", " >> large_template.json
echo "          \"中文试一下;\" " >> large_template.json
echo "        ] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"L2NoVlanNetwork${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::L2NoVlanNetwork\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testl2novlannetwork\", " >> large_template.json
echo "        \"description\": \"Novlan 二层网络\", " >> large_template.json
echo "        \"resourceUuid\":\"testuuid\", " >> large_template.json
echo "        \"zoneUuid\": { " >> large_template.json
echo "          \"Ref\": \"ZoneUuid${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"physicalInterface\": \"eth${i}\", " >> large_template.json
echo "        \"type\":\"test\", " >> large_template.json
echo "        \"timeout\":200, " >> large_template.json
echo "        \"systemTags\": [ " >> large_template.json
echo "          \"l2novlansystemtags\", " >> large_template.json
echo "          \"l2novlansystemtages2\" " >> large_template.json
echo "        ], " >> large_template.json
echo "        \"userTags\": [ " >> large_template.json
echo "          \"l2novlansertages1\", " >> large_template.json
echo "          \"l2novlanpoolertages2\", " >> large_template.json
echo "          \"中文试一下;\" " >> large_template.json
echo "        ] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"L2VlanNetwork${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::L2VlanNetwork\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testl2vlannetwork${i}\", " >> large_template.json
echo "        \"description\":\"l2vlannetwork\", " >> large_template.json
echo "        \"resourceUuid\":\"testuuid\", " >> large_template.json
echo "        \"zoneUuid\": { " >> large_template.json
echo "          \"Ref\": \"ZoneUuid${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"physicalInterface\": { " >> large_template.json
echo "          \"Ref\": \"L2Interface${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"timeout\":100, " >> large_template.json
echo "        \"systemTags\": [ " >> large_template.json
echo "          \"l2vlansystemtags\", " >> large_template.json
echo "          \"l2vlansystemtages2\" " >> large_template.json
echo "        ], " >> large_template.json
echo "        \"userTags\": [ " >> large_template.json
echo "          \"l2vlansertages1\", " >> large_template.json
echo "          \"l2vlanpoolertages2\", " >> large_template.json
echo "          \"中文试一下;\" " >> large_template.json
echo "        ] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"L2VxlanNetwork${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::L2VxlanNetwork\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testl2vxlannetwork${i}\", " >> large_template.json
echo "        \"description\":\"vxlannetwork\", " >> large_template.json
echo "        \"resourceUuid\":\"testuuid\", " >> large_template.json
echo "        \"type\":\"test\", " >> large_template.json
echo "        \"zoneUuid\": { " >> large_template.json
echo "          \"Ref\": \"ZoneUuid${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"physicalInterface\": { " >> large_template.json
echo "          \"Ref\": \"L2Interface${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"timeout\":100, " >> large_template.json
echo "        \"systemTags\": [ " >> large_template.json
echo "          \"l2vxlansystemtags\", " >> large_template.json
echo "          \"l2vxlansystemtages2\" " >> large_template.json
echo "        ], " >> large_template.json
echo "        \"userTags\": [ " >> large_template.json
echo "          \"l2vxlansertages1\", " >> large_template.json
echo "          \"l2vxlanpoolertages2\", " >> large_template.json
echo "          \"中文试一下;\" " >> large_template.json
echo "        ] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"L3Network${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::L3Network\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testl3network${i}\", " >> large_template.json
echo "        \"description\": \"l3network\", " >> large_template.json
echo "        \"dnsDomain\": \"8.8.8.8\", " >> large_template.json
echo "        \"l2NetworkUuid\": \"uuid\", " >> large_template.json
echo "        \"resourceUuid\":\"testuuid\", " >> large_template.json
echo "        \"system\":false, " >> large_template.json
echo "        \"type\":\"L3BasicNetwork\", " >> large_template.json
echo "        \"category\":\"Private\", " >> large_template.json
echo "        \"timeout\":100, " >> large_template.json
echo "        \"systemTags\": [ " >> large_template.json
echo "          \"l2vxlansystemtags\", " >> large_template.json
echo "          \"l2vxlansystemtages2\" " >> large_template.json
echo "        ], " >> large_template.json
echo "        \"userTags\": [ " >> large_template.json
echo "          \"l2vxlansertages1\", " >> large_template.json
echo "          \"l2vxlanpoolertages2\", " >> large_template.json
echo "          \"中文试一下;\" " >> large_template.json
echo "        ] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"VRouterRouteTable${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::VRouterRouteTable\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testVrouterRouTable${i}\", " >> large_template.json
echo "        \"description\": \"VrouterRouteTable\", " >> large_template.json
echo "        \"resourceUuid\": \"testuuid\", " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\":[\"test\"], " >> large_template.json
echo "        \"userTags\":[\"test\"] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"VpcVRouter${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::VpcVRouter\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testvpcvrouter${i}\", " >> large_template.json
echo "        \"description\": \"vpc vrouter\", " >> large_template.json
echo "        \"virtualRouterOfferingUuid\": \"Todo\", " >> large_template.json
echo "        \"resourceUuid\":\"uuid\", " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\":[\"test\"], " >> large_template.json
echo "        \"userTags\":[\"test\"] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"SecurityGroup${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::SecurityGroup\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testsecurityGroup${i}\", " >> large_template.json
echo "        \"description\": \"安全组\", " >> large_template.json
echo "        \"resourceUuid\": \"testuuid\", " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\":[\"test\"], " >> large_template.json
echo "        \"userTags\":[\"test\"] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"SecurityGroupRule${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::SecurityGroupRule\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"remoteSecurityGroupUuids\":[\"remotesguuid\"], " >> large_template.json
echo "        \"securityGroupUuid\": \"sguuid\", " >> large_template.json
echo "        \"rules\":[\"rule1\"], " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\":[\"test\"], " >> large_template.json
echo "        \"userTags\":[\"test\"] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"Vip${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::Vip\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testvip${i}\", " >> large_template.json
echo "        \"description\": \"vip\", " >> large_template.json
echo "        \"allocatorStrategy\":\"Random\", " >> large_template.json
echo "        \"l3NetworkUuid\": { " >> large_template.json
echo "          \"Fn::GetAtt\": [ " >> large_template.json
echo "            \"L3Network${i}\", " >> large_template.json
echo "            \"uuid\" " >> large_template.json
echo "          ] " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"requiredIp\":\"10.141.23.21\", " >> large_template.json
echo "        \"resourceUuid\": \"testuuid\", " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\":[\"test\"], " >> large_template.json
echo "        \"userTags\":[\"test\"] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"Eip${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::Eip\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testeip\", " >> large_template.json
echo "        \"description\": \"eip\", " >> large_template.json
echo "        \"vipUuid\": { " >> large_template.json
echo "          \"Fn::GetAtt\": [ " >> large_template.json
echo "            \"Vip${i}\", " >> large_template.json
echo "            \"uuid\" " >> large_template.json
echo "          ] " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"resourceUuid\": \"testuuid\", " >> large_template.json
echo "        \"vmNicUuid\":\"vmNicUuid\", " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\":[\"test\"], " >> large_template.json
echo "        \"userTags\":[\"test\"] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"PortForwardingRule${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::PortForwardingRule\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testPortForwardingRule\", " >> large_template.json
echo "        \"description\": \"pf\", " >> large_template.json
echo "        \"allowedCidr\": \"192.168.24.0/24\", " >> large_template.json
echo "        \"vipUuid\": { " >> large_template.json
echo "          \"Fn::GetAtt\": [ " >> large_template.json
echo "            \"Vip${i}\", " >> large_template.json
echo "            \"uuid\" " >> large_template.json
echo "          ] " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"protocolType\": \"TCP\", " >> large_template.json
echo "        \"vipUuid\": \"vipuuid\", " >> large_template.json
echo "        \"vmNicUuid\": \"vmnicuuid\", " >> large_template.json
echo "        \"resourceUuid\": \"testuuid\", " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\":[\"test\"], " >> large_template.json
echo "        \"userTags\":[\"test\"] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"LoadBalancer${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::LoadBalancer\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testLoadBalancer${i}\", " >> large_template.json
echo "        \"description\":\"lb\", " >> large_template.json
echo "        \"resourceUuid\":\"testuuid\", " >> large_template.json
echo "        \"vipUuid\": { " >> large_template.json
echo "          \"Fn::GetAtt\": [ " >> large_template.json
echo "            \"Vip${i}\", " >> large_template.json
echo "            \"uuid\" " >> large_template.json
echo "          ] " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\":[\"test\"], " >> large_template.json
echo "        \"userTags\":[\"test\"] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"LoadBalancerListener${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::LoadBalancerListener\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testLocaBalancerListerner${i}\", " >> large_template.json
echo "        \"description\":\"lbl\", " >> large_template.json
echo "        \"loadBalancerUuid\": { " >> large_template.json
echo "          \"Fn::GetAtt\": [ " >> large_template.json
echo "            \"LoadBalancer${i}\", " >> large_template.json
echo "            \"uuid\" " >> large_template.json
echo "          ] " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"loadBalancerPort\": { " >> large_template.json
echo "          \"Ref\": \"LoadBalancerPort${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"protocol\":\"TCP\", " >> large_template.json
echo "        \"resourceUuid\":\"testuuid\", " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\":[\"test\"], " >> large_template.json
echo "        \"userTags\":[\"test\"] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"IPsecConnection${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::IPsecConnection\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"testIPsecConnection\", " >> large_template.json
echo "        \"description\":\"IPsec\", " >> large_template.json
echo "        \"peerAddress\": { " >> large_template.json
echo "          \"Ref\": \"PeerAddress${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"authKey\": { " >> large_template.json
echo "          \"Ref\": \"AuthKey${i}\" " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"vipUuid\": { " >> large_template.json
echo "          \"Fn::GetAtt\": [ " >> large_template.json
echo "            \"Vip${i}\", " >> large_template.json
echo "            \"uuid\" " >> large_template.json
echo "          ] " >> large_template.json
echo "        }, " >> large_template.json
echo "        \"l3NetworkUuid\":\"l3uuid\", " >> large_template.json
echo "        \"peerCidrs\":[\"192.168.100.0/24\"], " >> large_template.json
echo "        \"authMode\":\"psk\", " >> large_template.json
echo "        \"ikeAuthAlgorithm\":\"sha1\", " >> large_template.json
echo "        \"ikeEncryptionAlgorithm\":\"aes-128\", " >> large_template.json
echo "        \"ikeDhGroup\":2, " >> large_template.json
echo "        \"policyAuthAlgorithm\":\"sha1\", " >> large_template.json
echo "        \"policyEncryptionAlgorithm\":\"aes-128\", " >> large_template.json
echo "        \"policyMode\":\"tunnel\", " >> large_template.json
echo "        \"pfs\":\"pfs\", " >> large_template.json
echo "        \"resourceUuid\":\"testuuid\", " >> large_template.json
echo "        \"transformProtocol\":\"esp\", " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\":[\"test\"], " >> large_template.json
echo "        \"userTags\":[\"test\"] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
echo "    \"VirtualRouterOffering${i}\": { " >> large_template.json
echo "      \"Type\": \"ZStack::Resource::VirtualRouterOffering\", " >> large_template.json
echo "      \"Properties\": { " >> large_template.json
echo "        \"name\": \"virtualrouteroffering\", " >> large_template.json
echo "        \"description\":\"vr-offering\", " >> large_template.json
echo "        \"resourceUuid\":\"testuuid\", " >> large_template.json
echo "        \"allocatorStrategy\":\"Mevoco\", " >> large_template.json
echo "        \"cpuNum\":2, " >> large_template.json
echo "        \"imageUuid\":\"imageuuid\", " >> large_template.json
echo "        \"isDefault\":false, " >> large_template.json
echo "        \"managementNetworkUuid\":\"mnnetworkUuid\", " >> large_template.json
echo "        \"memorySize\":1124774006935781000, " >> large_template.json
echo "        \"publicNetworkUuid\":\"pubuuid\", " >> large_template.json
echo "        \"sortKey\":1, " >> large_template.json
echo "        \"type\":\"ApplianceVm\", " >> large_template.json
echo "        \"zoneUuid\":\"zoneuuid\", " >> large_template.json
echo "        \"timeout\": 100, " >> large_template.json
echo "        \"systemTags\":[\"test\"], " >> large_template.json
echo "        \"userTags\":[\"test\"] " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
	let i=${i}+1
	
	if [ $i -eq $m ];then
	    break
	fi
done

echo "  }, " >> large_template.json
echo "  \"Outputs\": { " >> large_template.json
i=1
while true
do
echo "round $i outputs"
echo "    \"InstanceOffering${i}\": { " >> large_template.json
echo "      \"Value\": { " >> large_template.json
echo "        \"Ref\": \"InstanceOffering${i}\" " >> large_template.json
echo "      } " >> large_template.json
echo "    }, " >> large_template.json
	let i=${i}+1
	
	if [ $i -eq $m ];then
	    break
	fi
done

echo "    \"IP\": { " >> large_template.json
echo "      \"Value\": { " >> large_template.json
echo "        \"Fn::Select\": [ " >> large_template.json
echo "          \"0\", " >> large_template.json
echo "          [ " >> large_template.json
echo "            \"ip\", " >> large_template.json
echo "            \"11\", " >> large_template.json
echo "            \"test\" " >> large_template.json
echo "          ] " >> large_template.json
echo "        ] " >> large_template.json
echo "      } " >> large_template.json
echo "    } " >> large_template.json
echo "  } " >> large_template.json
echo "}" >> large_template.json
