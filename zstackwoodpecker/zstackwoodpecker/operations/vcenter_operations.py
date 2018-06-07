'''

All vcenter operations for test.

@author: SyZhao
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as account_operations
import zstackwoodpecker.operations.resource_operations as res_ops
import os



def add_vcenter(name, domain_name, username, password, https, zone_uuid, timeout=240000, session_uuid=None):
    action = api_actions.AddVCenterAction()
    action.name = name
    action.domainName = domain_name
    action.username = username
    action.password = password
    action.https = https
    action.zoneUuid = zone_uuid
    action.timeout = timeout
    test_util.action_logger('Add VCenter')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory


def delete_vcenter(vcenter_uuid, timeout=240000, session_uuid=None):
    action = api_actions.DeleteVCenterAction()
    action.uuid = vcenter_uuid
    action.timeout = timeout
    test_util.action_logger('Delete VCenter [uuid:] %s' % vcenter_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def sync_vcenter(vcenter_uuid, session_uuid=None):
    action = api_actions.SyncVCenterAction()
    action.uuid = vcenter_uuid
    test_util.action_logger('Sync vcenter %s' % vcenter_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt   

def lib_get_vcenter_primary_storage_by_name(ps_name):
    cond = res_ops.gen_query_conditions("name", '=', ps_name)
    vcps_inv = res_ops.query_resource(res_ops.VCENTER_PRIMARY_STORAGE, cond)
    if vcps_inv:
        return vcps_inv[0]
    
def lib_get_vcenter_backup_storage_by_name(bs_name):
    cond = res_ops.gen_query_conditions("name", '=', bs_name)
    vcbs_inv = res_ops.query_resource(res_ops.VCENTER_BACKUP_STORAGE, cond)
    if vcbs_inv:
        return vcbs_inv[0]

def lib_get_vcenter_cluster_by_name(cl_name):
    cond = res_ops.gen_query_conditions("name", '=', cl_name)
    cluster_inv = res_ops.query_resource(res_ops.VCENTER_CLUSTER, cond)
    if cluster_inv:
        return cluster_inv[0]

def lib_get_vcenter_l2_by_name(l2_name):
    cond = res_ops.gen_query_conditions("name", '=', l2_name)
    l2_inv = res_ops.query_resource(res_ops.L2_NETWORK, cond)
    if l2_inv:
        return l2_inv[0]

def lib_get_vcenter_l2_by_name_and_cluster(l2_name, cluster_uuid):
    cond = res_ops.gen_query_conditions("name", '=', l2_name)
    cond = res_ops.gen_query_conditions('attachedClusterUuids', '=', cluster_uuid, cond)
    l2_inv = res_ops.query_resource(res_ops.L2_NETWORK, cond)
    if l2_inv:
        return l2_inv[0]

def lib_get_vcenter_l3_by_name(l3_name):
    cond = res_ops.gen_query_conditions("name", '=', l3_name)
    l3_inv = res_ops.query_resource(res_ops.L3_NETWORK, cond)
    if l3_inv:
        return l3_inv[0]

def lib_get_vcenter_l3_by_name_and_l2(l3_name, l2_uuid):
    cond = res_ops.gen_query_conditions("name", '=', l3_name)
    cond = res_ops.gen_query_conditions('l2NetworkUuid', '=', l2_uuid, cond)
    l3_inv = res_ops.query_resource(res_ops.L3_NETWORK, cond)
    if l3_inv:
        return l3_inv[0]

def lib_get_vcenter_by_name(vc_name):
    cond = res_ops.gen_query_conditions("name", '=', vc_name)
    vc_inv = res_ops.query_resource(res_ops.VCENTER, cond)
    if vc_inv:
        return vc_inv[0]

def lib_get_vcenter_host_by_ip(ip):
    cond = res_ops.gen_query_conditions("managementIp", '=', ip)
    host_inv = res_ops.query_resource(res_ops.HOST, cond)
    if host_inv:
        return host_inv[0]

def lib_get_vm_by_name(name):
    cond = res_ops.gen_query_conditions('name', '=', name)
    vms = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
    if vms:
        return vms[0]

def lib_get_vcenter_dvswitches(vc_uuid):
    return res_ops.get_resource_by_get(res_ops.VCENTER_DVSWITCHES, None, vc_uuid)[0]

def lib_get_root_image_by_name(name):
    cond = res_ops.gen_query_conditions('mediaType', '=', 'RootVolumeTemplate')
    cond = res_ops.gen_query_conditions('status', '!=', 'Deleted', cond)
    cond = res_ops.gen_query_conditions('name', '=', name, cond)
    return res_ops.query_resource(res_ops.IMAGE, cond)[0]

def connect_vcenter(ip):
    from pyVim import connect
    vcenter = ip
    vcenteruser = "administrator@vsphere.local"
    vcenterpwd = "Testing%123"
    SI = connect.SmartConnectNoSSL(host=vcenter, user=vcenteruser, pwd=vcenterpwd, port=443)
    if not SI:
        test_util.test_fail("Unable to connect to the vCenter %s" % vcenter)
    return SI


def get_obj(content, vimtype, name=None):
    from pyVmomi import vim
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    if name:
        for c in container.view:
            if c.name == name:
                obj = c
                return obj
    return container.view


def create_datacenter(service_instance, name):
    folder = service_instance.content.rootFolder
    datacenter = folder.CreateDatacenter(name=name)
    return datacenter


def get_datacenter(content, name=None):
    from pyVmomi import vim
    dc = get_obj(content, [vim.Datacenter], name=name)
    if isinstance(dc, list):
        test_util.test_logger("do not find datacenter named %s, now return all datacenter" % name)
        return dc
    return [dc]


def create_cluster(datacenter=None, name='cluster_x'):
    from pyVmomi import vim
    cluster_spec = vim.cluster.ConfigSpecEx()
    host_folder = datacenter.hostFolder
    cluster = host_folder.CreateClusterEx(name=name, spec=cluster_spec)
    return cluster


def get_cluster(content, name=None):
    from pyVmomi import vim
    cluster = get_obj(content, [vim.ClusterComputeResource], name=name)
    if isinstance(cluster, list):
        test_util.test_logger("do not find cluster named %s, now return all cluster" % name)
        return cluster
    return [cluster]

def remove_cluster(cluster):
    from pyVim import task
    TASK = cluster.Destroy_Task()
    task.WaitForTask(TASK)

def create_dvswitch(datacenter=None, name='DvSwitch0', DVSCreateSpec=None):
    from pyVmomi import vim
    from pyVim import task
    if not DVSCreateSpec:
        DVSCreateSpec = vim.DistributedVirtualSwitch.CreateSpec(
            configSpec=vim.DistributedVirtualSwitch.ConfigSpec(name=name)
        )
    folder = datacenter.networkFolder
    Task = folder.CreateDVS_Task(spec=DVSCreateSpec)
    task.WaitForTask(Task)
    return Task.info.result

def add_dportgroup(dvswitch, name='dpg_0', vlanId=0):
    from pyVmomi import vim
    from pyVim import task
    vlan = vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec()
    vlan.vlanId = int(vlanId)
    defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
    defaultPortConfig.vlan = vlan

    DVPortgroupConfigSpec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
    DVPortgroupConfigSpec.name = name
    DVPortgroupConfigSpec.type = 'ephemeral'
    DVPortgroupConfigSpec.autoExpand = False
    DVPortgroupConfigSpec.defaultPortConfig = defaultPortConfig

    Task = dvswitch.CreateDVPortgroup_Task(spec=DVPortgroupConfigSpec)
    task.WaitForTask(Task)
    return Task.info.result


def add_host(cluster, ip):
    from pyVmomi import vim
    from pyVim import task
    host_spec = vim.host.ConnectSpec(hostName=ip,
                                     userName="root",
                                     password="password",
                                     sslThumbprint='52:DF:8F:E5:37:43:57:7B:65:CC:BC:97:DE:EC:80:AE:96:FC:49:11',
                                     force=False)
    TASK = cluster.AddHost_Task(spec=host_spec, asConnected=True)
    task.WaitForTask(TASK)
    host_inf = TASK.info.result
    return host_inf


def get_host(content, name=None):
    from pyVmomi import vim
    host = get_obj(content, [vim.HostSystem], name=name)
    if isinstance(host, list):
        test_util.test_logger("do not find host named %s, now return all host" % name)
        return host
    return [host]

def disconnect_host(host_obj):
    from pyVim import task
    Task = host_obj.DisconnectHost_Task()
    task.WaitForTask(Task)

def remove_host(host_obj):
    from pyVim import task
    disconnect_host(host_obj)
    TASK = host_obj.Destroy_Task()
    task.WaitForTask(TASK)
    
def get_host_networkSystem(host):
    return host.configManager.networkSystem

def find_host_by_vm(content, vm_name):
    vc_vm = get_vm(content, vm_name)[0]
    return vc_vm.summary.runtime.host.name

def add_vswitch(host, name):
    from pyVmomi import vim
    nics = get_free_nics(host)
    if not nics:
        test_util.test_fail("no available nic to create vswitch")
    brige = vim.host.VirtualSwitch.BondBridge()
    brige.nicDevice = [nics[0], ]
    spec = vim.host.VirtualSwitch.Specification()
    spec.bridge = brige
    spec.numPorts = 128
    get_host_networkSystem(host).AddVirtualSwitch(vswitchName=name, spec=spec)


def dvswitch_add_host(dvswitch, host):
    from pyVmomi import vim
    from pyVim import task
    nics = get_free_nics(host)
    if not nics:
        test_util.test_fail("no available nic to add dvswitch")
    backing = vim.dvs.HostMember.PnicBacking(pnicSpec=[vim.dvs.HostMember.PnicSpec(pnicDevice=nics[0]), ])
    host_config = vim.dvs.HostMember.ConfigSpec(host=host, backing=backing, operation='add')
    config = vim.DistributedVirtualSwitch.ConfigSpec(host=[host_config, ], configVersion=dvswitch.config.configVersion)
    Task = dvswitch.ReconfigureDvs_Task(spec=config)
    task.WaitForTask(Task)


def remove_vswitch(host, name=None):
    nics = get_busy_nics(host)
    for i in nics:
        if ''.join(i.values()) == name:
            get_host_networkSystem(host).RemoveVirtualSwitch(name)
            return
    test_util.test_fail("no vswicth named %s" % name)

def remove_portgroup(host, name=None):
    get_host_networkSystem(host).RemovePortGroup(name)


def get_all_nics(host):
    _pnic = get_host_networkSystem(host).networkInfo.pnic
    pnic = [i.device for i in _pnic]
    return pnic


def get_free_nics(host):
    all_nics = get_all_nics(host)
    busy_nics = get_busy_nics(host)
    for i in busy_nics:
        all_nics.remove(''.join(i.keys()))
    return all_nics


def get_busy_nics(host):
    _vswitch = get_host_networkSystem(host).networkInfo.vswitch
    nics = [{(str(i.spec.bridge.nicDevice).split("\n")[1]).strip(" '"): i.name} for i in _vswitch]
    _proxyswitchs = get_host_networkSystem(host).networkInfo.proxySwitch
    if _proxyswitchs:
        for _proxyswitch in _proxyswitchs:
            nics.append({_proxyswitch.spec.backing.pnicSpec[0].pnicDevice: _proxyswitch.dvsName})
    return nics


def add_portgroup(host=None, vswitch="vSwitch0", name=None, vlanId=0):
    from pyVmomi import vim
    portgroup_spec = vim.host.PortGroup.Specification()
    portgroup_spec.vswitchName = vswitch
    portgroup_spec.name = name
    portgroup_spec.vlanId = int(vlanId)
    network_policy = vim.host.NetworkPolicy()
    network_policy.security = vim.host.NetworkPolicy.SecurityPolicy()
    network_policy.security.allowPromiscuous = True
    network_policy.security.macChanges = False
    network_policy.security.forgedTransmits = False
    portgroup_spec.policy = network_policy

    get_host_networkSystem(host).AddPortGroup(portgroup_spec)


def enter_maintenance_mode(host, timeout=60):
    from pyVim import task
    TASK = host.EnterMaintenanceMode_Task(timeout=timeout)
    task.WaitForTask(TASK)
    host_inf = TASK.info.result
    return host_inf


def exit_maintenance_mode(host, timeout=60):
    from pyVim import task
    TASK = host.ExitMaintenanceMode(timeout=timeout)
    task.WaitForTask(TASK)
    host_inf = TASK.info.result
    return host_inf

def add_disk(vm, disk_size):
    """
    :param vm: Virtual Machine Object
    :param disk_size: disk size, in GB
    """
    from pyVmomi import vim
    from pyVim import task
    spec = vim.vm.ConfigSpec()
    # get all disks on a VM, set unit_number to the next available
    unit_number = 0
    for dev in vm.config.hardware.device:
        if hasattr(dev.backing, 'fileName'):
            unit_number = int(dev.unitNumber) + 1
            # unit_number 7 reserved for scsi controller
            if unit_number == 7:
                unit_number += 1
            if unit_number >= 16:
                print "we don't support this many disks"
                return
        if isinstance(dev, vim.vm.device.VirtualSCSIController):
            controller = dev
    # add disk here
    dev_changes = []
    new_disk_kb = int(disk_size) * 1024 * 1024
    disk_spec = vim.vm.device.VirtualDeviceSpec()
    disk_spec.fileOperation = "create"
    disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    disk_spec.device = vim.vm.device.VirtualDisk()
    disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
    disk_spec.device.backing.thinProvisioned = True
    disk_spec.device.backing.diskMode = 'persistent'
    disk_spec.device.unitNumber = unit_number
    disk_spec.device.capacityInKB = new_disk_kb
    disk_spec.device.controllerKey = controller.key
    dev_changes.append(disk_spec)
    spec.deviceChange = dev_changes
    TASK = vm.ReconfigVM_Task(spec=spec)
    task.WaitForTask(TASK)
    print "%sGB disk added to %s" % (disk_size, vm.config.name)

def delete_virtual_disk(vm, disk_number):
    """ Deletes virtual Disk based on disk number
    :param vm: Virtual Machine Object
    :param disk_number: Hard Disk Unit Number
    :return: True if success
    """
    from pyVmomi import vim
    from pyVim import task
    hdd_label = 'Hard disk ' + str(disk_number)
    virtual_hdd_device = None
    for dev in vm.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualDisk) and dev.deviceInfo.label == hdd_label:
            virtual_hdd_device = dev
    if not virtual_hdd_device:
        raise RuntimeError('Virtual {} could not be found.'.format(virtual_hdd_device))

    virtual_hdd_spec = vim.vm.device.VirtualDeviceSpec()
    virtual_hdd_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
    virtual_hdd_spec.device = virtual_hdd_device

    spec = vim.vm.ConfigSpec()
    spec.deviceChange = [virtual_hdd_spec]
    TASK = vm.ReconfigVM_Task(spec=spec)
    task.WaitForTask(TASK)
    return True

def get_data_volume_attach_to_vm(vm):
    from pyVmomi import vim
    disk = []
    for dev in vm.config.hardware.device:
      if isinstance(dev, vim.vm.device.VirtualDisk) and dev.deviceInfo.label != 'Hard disk 1':
         disk.append(dev.backing.fileName)
    return disk

def get_vm(content, name=None):
    from pyVmomi import vim
    vm = get_obj(content, [vim.VirtualMachine], name=name)
    if isinstance(vm, list):
        test_util.test_logger("do not find vm named %s, now return all vm" % name)
        return vm
    return [vm]

def destroy_vm(vm):
    from pyVim import task
    if vm.runtime.powerState == 'poweredOn':
        powerOff_vm(vm)
    TASK = vm.Destroy_Task()
    task.WaitForTask(TASK)

def powerOff_vm(vm):
    from pyVim import task
    Task = vm.PowerOffVM_Task()
    task.WaitForTask(Task)

def get_datastore_type(vcenter):
    SI = connect_vcenter(vcenter)
    content = SI.RetrieveContent()
    host = get_host(content)[0]
    if host.configManager.storageSystem.fileSystemVolumeInfo.mountInfo[0].volume.local:
        type = 'local'  
    else:
        type = 'iscsi'     
    return type

def enable_vmotion(host_obj):
    vnic = host_obj.configManager.virtualNicManager
    vnic.SelectVnicForNicType(nicType='vmotion',device='vmk0')


 