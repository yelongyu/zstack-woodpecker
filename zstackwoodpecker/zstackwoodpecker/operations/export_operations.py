'''
Export ZStack database configuration to an xmlobject

@author: YYK
'''

import xml.etree.cElementTree as etree
import sys
import traceback

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as account_operations

import zstacklib.utils.xmlobject as xmlobject
import xml.dom.minidom as minidom

def set_xml_item_attr(parent, item_name, value):
    if not value:
        return

    if isinstance(value, int):
        value = str(value)

    parent.set(item_name, value)

def add_xml_item_value(parent, item_name, value):
    item = etree.SubElement(parent, item_name)
    item.text = value

def add_zone_config(root_xml, pre_zone_setting, session_uuid = None):
    cond = res_ops.gen_query_conditions('uuid', '!=', '0')
    zones = res_ops.query_resource(res_ops.ZONE, cond, session_uuid)
    zones_xml = etree.SubElement(root_xml, "zones")

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond, session_uuid)

    zones_dict = {}
    if pre_zone_setting:
        zones_list = pre_zone_setting.get_child_node_as_list('zone')
        for zone in zones_list:
            zones_dict[zone.name_] = zone

    for zone in zones:
        pre_zone = None
        if zones_dict.has_key(zone.name):
            pre_zone = zones_dict[zone.name]

        zone_xml = etree.SubElement(zones_xml, "zone")
        set_xml_item_attr(zone_xml, 'name', zone.name)
        set_xml_item_attr(zone_xml, 'type', zone.type)
        set_xml_item_attr(zone_xml, 'uuid', zone.uuid)
        set_xml_item_attr(zone_xml, 'description', zone.description)
        
        #add_backup_stroage_ref(zone_xml, session_uuid)
        for bs in bss:
            if zone.uuid in bs.attachedZoneUuids:
                add_xml_item_value(zone_xml, 'backupStorageRef', bs.name)

        add_primary_storage_config(zone_xml, zone.uuid, pre_zone.primaryStorages, session_uuid)

        if pre_zone:
            pre_cluster_setting = pre_zone.clusters
        else:
            pre_cluster_setting = None

        add_cluster_config(zone_xml, pre_cluster_setting, zone.uuid, \
                session_uuid)
        add_l2_network_config(zone_xml, zone.uuid, session_uuid)

def add_cluster_config(zone_xml, pre_cluster_setting, zone_uuid, \
        session_uuid = None):
    clusters_xml = etree.SubElement(zone_xml, "clusters")
    cond = res_ops.gen_query_conditions('zoneUuid', '=', zone_uuid)
    clusters = res_ops.query_resource(res_ops.CLUSTER, cond, session_uuid)

    clusters_dict = {}
    if pre_cluster_setting:
        clusters_list = pre_cluster_setting.get_child_node_as_list('cluster')
        for cluster in clusters_list:
            clusters_dict[cluster.name_] = cluster

    cond = res_ops.gen_query_conditions('uuid', '!=', '0')
    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond, \
            session_uuid)

    l2s = res_ops.query_resource(res_ops.L2_NETWORK, cond, session_uuid)

    for cluster in clusters:
        cluster_xml = etree.SubElement(clusters_xml, "cluster")
        set_xml_item_attr(cluster_xml, 'name', cluster.name)
        set_xml_item_attr(cluster_xml, 'description', cluster.description)
        set_xml_item_attr(cluster_xml, 'hypervisorType', cluster.hypervisorType)
        if clusters_dict.has_key(cluster.name):
            pre_hosts_setting = clusters_dict[cluster.name].hosts
        else:
            pre_hosts_setting = None

        add_host_config(cluster_xml, pre_hosts_setting, cluster.uuid, \
                session_uuid)

        for ps in pss:
            if cluster.uuid in ps.attachedClusterUuids:
                add_xml_item_value(cluster_xml, 'primaryStorageRef', ps.name)

        for l2 in l2s:
            if cluster.uuid in l2.attachedClusterUuids:
                add_xml_item_value(cluster_xml, 'l2NetworkRef', l2.name)

def add_host_config(cluster_xml, pre_hosts_setting, cluster_uuid, \
        session_uuid = None):
    hosts_xml = etree.SubElement(cluster_xml, "hosts")
    cond = res_ops.gen_query_conditions('clusterUuid', '=', cluster_uuid)
    hosts = res_ops.query_resource(res_ops.HOST, cond, session_uuid)
    hosts_dict = {}
    if pre_hosts_setting:
        hosts_list = pre_hosts_setting.get_child_node_as_list('host')
        for host in hosts_list:
            hosts_dict[host.managementIp_] = host

    for host in hosts:
        host_xml = etree.SubElement(hosts_xml, "host")
        set_xml_item_attr(host_xml, 'name', host.name)
        set_xml_item_attr(host_xml, 'description', host.description)
        set_xml_item_attr(host_xml, 'managementIp', host.managementIp)
        #if host.type == 'hypervisorType':
        if hosts_dict.has_key(host.managementIp):
            set_xml_item_attr(host_xml, 'username', \
                    hosts_dict[host.managementIp].username__)
            set_xml_item_attr(host_xml, 'password', \
                    hosts_dict[host.managementIp].password__)

def add_l2_network_config(zone_xml, zone_uuid, session_uuid = None):
    l2s_xml = etree.SubElement(zone_xml, "l2Networks")
    add_l2_no_vlan_network_config(l2s_xml, zone_uuid, session_uuid)
    add_l2_vlan_network_config(l2s_xml, zone_uuid, session_uuid)

def add_l2_no_vlan_network_config(l2s_xml, zone_uuid, session_uuid = None):
    cond = res_ops.gen_query_conditions('type', '=', 'L2NoVlanNetwork')
    cond = res_ops.gen_query_conditions('zoneUuid', '=', zone_uuid, cond)
    l2s = res_ops.query_resource(res_ops.L2_NETWORK, cond, session_uuid)

    for l2 in l2s:
        l2_xml = etree.SubElement(l2s_xml, "l2NoVlanNetwork")
        set_xml_item_attr(l2_xml, 'name', l2.name)
        set_xml_item_attr(l2_xml, 'description', l2.description)
        set_xml_item_attr(l2_xml, 'physicalInterface', l2.physicalInterface)
        add_l3_network_config(l2_xml, l2.uuid, session_uuid)

def add_l3_network_config(l2_xml, l2_uuid, session_uuid = None):
    cond = res_ops.gen_query_conditions('l2NetworkUuid', '=', l2_uuid)
    l3s = res_ops.query_resource(res_ops.L3_NETWORK, cond, session_uuid)
    l3s_xml = etree.SubElement(l2_xml, "l3Networks")
    for l3 in l3s:
        if l3.type == 'L3BasicNetwork':
            l3_xml = etree.SubElement(l3s_xml, "l3BasicNetwork")
            set_xml_item_attr(l3_xml, 'name', l3.name)
            set_xml_item_attr(l3_xml, 'description', l3.description)
            add_ip_range(l3_xml, l3.ipRanges)
            add_dns(l3_xml, l3.dns)
            add_network_service(l3_xml, l3.networkServices, session_uuid)

def add_ip_range(l3_xml, ip_ranges):
    for ip_range in ip_ranges:
        ip_range_xml = etree.SubElement(l3_xml, "ipRange")
        set_xml_item_attr(ip_range_xml, 'name', ip_range.name)
        set_xml_item_attr(ip_range_xml, 'description', ip_range.description)
        set_xml_item_attr(ip_range_xml, 'startIp', ip_range.startIp)
        set_xml_item_attr(ip_range_xml, 'endIp', ip_range.endIp)
        set_xml_item_attr(ip_range_xml, 'gateway', ip_range.gateway)
        set_xml_item_attr(ip_range_xml, 'netmask', ip_range.netmask)

def add_dns(l3_xml, dnss):
    for dns in dnss:
        add_xml_item_value(l3_xml, 'dns', dns)

def add_network_service(l3_xml, networkServices, session_uuid = None):
    service_provider_dict = {}

    for network_service in networkServices:
        if not service_provider_dict.has_key(network_service.networkServiceProviderUuid):
            cond = res_ops.gen_query_conditions('uuid', '=', \
                    network_service.networkServiceProviderUuid)
            service = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, cond, session_uuid)[0]
            service_name = service.name
            service_xml = etree.SubElement(l3_xml, 'networkService')
            set_xml_item_attr(service_xml, 'provider', service_name)
            service_provider_dict[network_service.networkServiceProviderUuid] =\
                    service_xml
        else:
            service_xml = service_provider_dict[network_service.networkServiceProviderUuid]

        add_xml_item_value(service_xml, 'serviceType', \
                network_service.networkServiceType)

def add_l2_vlan_network_config(l2s_xml, zone_uuid, session_uuid = None):
    cond = res_ops.gen_query_conditions('type', '=', 'L2VlanNetwork')
    cond = res_ops.gen_query_conditions('zoneUuid', '=', zone_uuid, cond)
    l2s = res_ops.query_resource(res_ops.L2_NETWORK, cond, session_uuid)

    for l2 in l2s:
        l2_xml = etree.SubElement(l2s_xml, "l2VlanNetwork")
        set_xml_item_attr(l2_xml, 'name', l2.name)
        set_xml_item_attr(l2_xml, 'description', l2.description)
        set_xml_item_attr(l2_xml, 'physicalInterface', l2.physicalInterface)
        set_xml_item_attr(l2_xml, 'vlan', l2.vlan)
        add_l3_network_config(l2_xml, l2.uuid, session_uuid)

def add_primary_storage_config(zone_xml, zone_uuid, pre_pss, session_uuid = None):
    pss_xml = etree.SubElement(zone_xml, "primaryStorages")
    cond = res_ops.gen_query_conditions('zoneUuid', '=', zone_uuid)
    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond, session_uuid)
    for ps in pss:
        if ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE:
            ps_xml = etree.SubElement(pss_xml, "nfsPrimaryStorage")
            set_xml_item_attr(ps_xml, 'name', ps.name)
            set_xml_item_attr(ps_xml, 'description', ps.description)
            set_xml_item_attr(ps_xml, 'url', ps.url)
        elif ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE:
            ps_xml = etree.SubElement(pss_xml, "cephPrimaryStorage")
            set_xml_item_attr(ps_xml, 'name', ps.name)
            set_xml_item_attr(ps_xml, 'description', ps.description)
            for pre_ps in pre_pss.get_child_node_as_list('cephPrimaryStorage'):
                if pre_ps.name__ == ps.name:
                    set_xml_item_attr(ps_xml, 'monUrls', pre_ps.monUrls)
                    break
        elif ps.type == inventory.LOCAL_STORAGE_TYPE:
            ps_xml = etree.SubElement(pss_xml, "localPrimaryStorage")
            set_xml_item_attr(ps_xml, 'name', ps.name)
            set_xml_item_attr(ps_xml, 'description', ps.description)
            set_xml_item_attr(ps_xml, 'url', ps.url)

def add_image_config(root_xml, original_images_setting, session_uuid = None):
    images_xml = etree.SubElement(root_xml, "images")
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    images = res_ops.query_resource(res_ops.IMAGE, cond, session_uuid)
    
    pre_images = {}
    if original_images_setting:
        pre_images_list = \
                original_images_setting.get_child_node_as_list('image')
        for pre_image in pre_images_list:
            pre_images[pre_image.url_] = pre_image

    for image in images:
        image_xml = etree.SubElement(images_xml, "image")
        set_xml_item_attr(image_xml, 'name', image.name)
        set_xml_item_attr(image_xml, 'description', image.description)
        set_xml_item_attr(image_xml, 'url', image.url)
        set_xml_item_attr(image_xml, 'format', image.format)
        set_xml_item_attr(image_xml, 'mediaType', image.mediaType)
        set_xml_item_attr(image_xml, 'guestOsType', image.guestOsType)
        set_xml_item_attr(image_xml, 'hypervisorType', image.hypervisorType)
        set_xml_item_attr(image_xml, 'bits', image.bits)
        if pre_images.has_key(image.url):
            set_xml_item_attr(image_xml, 'username', \
                    pre_images[image.url].username__)
            set_xml_item_attr(image_xml, 'password', \
                    pre_images[image.url].password__)
        for bs in image.backupStorageRefs:
            cond = res_ops.gen_query_conditions('uuid', '=', \
                    bs.backupStorageUuid)
            bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond, \
                    session_uuid)[0]
            add_xml_item_value(image_xml, 'backupStorageRef', bs.name)

def add_disk_offering_config(root_xml, session_uuid = None):
    disk_offerings_xml = etree.SubElement(root_xml, 'diskOfferings')
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    disk_offerings = res_ops.query_resource(res_ops.DISK_OFFERING, cond, \
            session_uuid)
    for disk_offering in disk_offerings:
        disk_offering_xml = etree.SubElement(disk_offerings_xml, 'diskOffering')
        set_xml_item_attr(disk_offering_xml, 'name', disk_offering.name)
        set_xml_item_attr(disk_offering_xml, 'description', \
                disk_offering.description)
        set_xml_item_attr(disk_offering_xml, 'diskSize', disk_offering.diskSize)

def add_sftp_backup_stroage_config(root_xml, bs_original_configs, \
        session_uuid = None):
    bss_xml = etree.SubElement(root_xml, 'backupStorages')
    cond = res_ops.gen_query_conditions('uuid', '!=', '0')
    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond, \
            session_uuid)
    for bs in bss:
        if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
            bs_xml = etree.SubElement(bss_xml, 'sftpBackupStorage')
            set_xml_item_attr(bs_xml, 'name', bs.name)
            set_xml_item_attr(bs_xml, 'description', bs.description)
            set_xml_item_attr(bs_xml, 'url', bs.url)
            set_xml_item_attr(bs_xml, 'hostname', bs.hostname)
            if bs_original_configs:
                for bs_o in \
                    bs_original_configs.get_child_node_as_list('sftpBackupStorage'):
                    if bs_o.name_ == bs.name:
                        #if backstorage names are same, there will be issue.
                        set_xml_item_attr(bs_xml, 'username', bs_o.username_)
                        set_xml_item_attr(bs_xml, 'password', bs_o.password_)
                        break
        elif bs.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
            bs_xml = etree.SubElement(bss_xml, 'cephBackupStorage')
            set_xml_item_attr(bs_xml, 'name', bs.name)
            set_xml_item_attr(bs_xml, 'description', bs.description)
            if bs_original_configs:
                for bs_o in bs_original_configs.get_child_node_as_list('cephBackupStorage'):
                    if bs_o.name_ == bs.name:
                        set_xml_item_attr(bs_xml, 'monUrls', bs_o.monUrls_)
                        break


def add_instance_offering_config(root_xml, session_uuid = None):
    ios_xml = etree.SubElement(root_xml, 'instanceOfferings')

    #add user type instance offering
    cond = res_ops.gen_query_conditions('type', '=', 'UserVm')
    user_ios = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond, \
            session_uuid)
    for user_io in user_ios:
        if user_io.state != 'Enabled':
            continue
        io_xml = etree.SubElement(ios_xml, 'instanceOffering')
        set_xml_item_attr(io_xml, 'name', user_io.name)
        set_xml_item_attr(io_xml, 'description', user_io.description)
        set_xml_item_attr(io_xml, 'memoryCapacity', user_io.memorySize)
        set_xml_item_attr(io_xml, 'cpuNum', user_io.cpuNum)
        set_xml_item_attr(io_xml, 'cpuSpeed', user_io.cpuSpeed)

    #add virtual router instance offering
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    vr_ios = res_ops.query_resource(res_ops.VR_OFFERING, cond, session_uuid)
    for vr_io in vr_ios:
        io_xml = etree.SubElement(ios_xml, 'virtualRouterOffering')
        set_xml_item_attr(io_xml, 'name', vr_io.name)
        set_xml_item_attr(io_xml, 'description', vr_io.description)
        set_xml_item_attr(io_xml, 'memoryCapacity', vr_io.memorySize)
        set_xml_item_attr(io_xml, 'cpuNum', vr_io.cpuNum)
        set_xml_item_attr(io_xml, 'cpuSpeed', vr_io.cpuSpeed)
        set_xml_item_attr(io_xml, 'isDefault', vr_io.isDefault)
        cond = res_ops.gen_query_conditions('uuid', '=', \
                vr_io.publicNetworkUuid)
        l3 = res_ops.query_resource(res_ops.L3_NETWORK, cond, session_uuid)
        if not l3:
            raise test_util.TestError('Not find L3 Network for [uuid:] %s' % \
                    vr_io.publicNetworkUuid)

        l3_ref = etree.SubElement(io_xml, 'publicL3NetworkRef')
        l3_ref.text = l3[0].name

        cond = res_ops.gen_query_conditions('uuid', '=', \
                vr_io.managementNetworkUuid)
        l3 = res_ops.query_resource(res_ops.L3_NETWORK, cond, session_uuid)
        add_xml_item_value(io_xml, 'managementL3NetworkRef', l3[0].name)

        cond = res_ops.gen_query_conditions('uuid', '=', vr_io.zoneUuid)
        zones = res_ops.query_resource(res_ops.ZONE, cond, session_uuid)
        add_xml_item_value(io_xml, 'zoneRef', zones[0].name)

        cond = res_ops.gen_query_conditions('uuid', '=', vr_io.imageUuid)
        imgs = res_ops.query_resource(res_ops.IMAGE, cond, session_uuid)
        add_xml_item_value(io_xml, 'imageRef', imgs[0].name)

def add_nodes_config(root_xml, nodes_original_config, session_uuid):
    nodes_xml = etree.SubElement(root_xml, 'nodes')
    cond = res_ops.gen_query_conditions('uuid', '!=', '0')
    nodes = res_ops.query_resource(res_ops.MANAGEMENT_NODE, cond, \
            session_uuid)

    nodes_setting = {}
    if nodes_original_config:
        nodes_list = nodes_original_config.get_child_node_as_list('node')
        for node in nodes_list:
            nodes_setting[node.ip_] = node

    for node in nodes:
        if nodes_setting.has_key(node.hostName):
            node_xml = etree.SubElement(nodes_xml, 'node')
            set_xml_item_attr(node_xml, 'name', \
                    nodes_setting[node.hostName].name__)
            set_xml_item_attr(node_xml, 'ip', node.hostName)
            set_xml_item_attr(node_xml, 'username', \
                    nodes_setting[node.hostName].username__)
            set_xml_item_attr(node_xml, 'password', \
                    nodes_setting[node.hostName].password__)
            set_xml_item_attr(node_xml, 'dockerImage', \
                    nodes_setting[node.hostName].dockerImage__)
            set_xml_item_attr(node_xml, 'description', \
                    nodes_setting[node.hostName].description__)
            set_xml_item_attr(node_xml, 'reserve', \
                    nodes_setting[node.hostName].reserve__)

def dump_zstack_deployment_config(deployConfig = None):
    '''
    deployConfig is the original zstack config. We need this conifg to set 
    username/password, as they are not get from ZStack API

    will return an xmlobject
    '''
    if not deployConfig:
        deployConfig = xmlobject.XmlObject('fake')

    root_xml = etree.Element("deployerConfig")
    session_uuid = account_operations.login_as_admin()
    try:
        add_nodes_config(root_xml, deployConfig.nodes__, session_uuid)
        add_sftp_backup_stroage_config(root_xml, \
                deployConfig.backupStorages__, session_uuid)
        add_instance_offering_config(root_xml, session_uuid)
        add_disk_offering_config(root_xml, session_uuid)
        add_image_config(root_xml, deployConfig.images__, session_uuid)
        add_zone_config(root_xml, deployConfig.zones, session_uuid)
    except Exception as e:
        test_util.test_logger('[Error] export zstack deployment configuration meets exception.')
        traceback.print_exc(file=sys.stdout)
        raise e
    finally:
        account_operations.logout(session_uuid)

    return root_xml

def export_zstack_deployment_config(deploy_config = None):
    root_xml = dump_zstack_deployment_config(deploy_config)
    return xmlobject.loads(etree.tostring(root_xml))

def export_zstack_deployment_config_to_file(deploy_config = None, \
        file_name = '/var/lib/zstack/current_deploy.xml'):
    xml_obj = dump_zstack_deployment_config(deploy_config)
    xml_string = etree.tostring(xml_obj, 'utf-8')
    xml_string = minidom.parseString(xml_string).toprettyxml(indent="  ")
    print xml_string

    open(file_name, 'w').write(xml_string)



