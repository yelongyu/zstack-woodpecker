import re
import collectd
import random

vm_instance = {}
#MAX_VALUE = 9223372036854775807
MAX_VALUE = 100
CPU_MAX_VALUE = 1000000000
VCPU_MAX_VALUE = 100000000

def get_prefix(full_string = None):
    m = re.match(r'vm_instance(\d+)',full_string)
    return m.group()

def get_suffix(full_string = None):
    m = re.match(r'vm_instance(\d+)_(\w+)',full_string)
    return m.group(2)

def fake_virt_config(config):

    for node in config.children:
        key = node.key.lower()
        val = node.values[0]
        global vm_instance

        if key.endswith('name') :
            temp_dict = {}

            temp_name = get_prefix(key)
            temp_key = get_suffix(key)
            temp_dict[temp_key] = val
            vm_instance[temp_name] = temp_dict
        elif key.endswith('cpu_num') or key.endswith('memory') or key.endswith('disks') or key.endswith('net_interfaces'):
            temp_key = get_suffix(key)
            temp_dict[temp_key] = val
        else:
            collectd.info('unknown config key %s for plugin virt' % key)

def fake_virt_read():

    virt_memory_type = ['actual_balloon', 'available', 'major_fault', 'minor_fault', 'rss', 'swap_in', 'swap_out', 'total', 'unused']
    virt_disk_type = ['disk_octets', 'disk_ops']
    virt_net_type = ['if_dropped', 'if_errors', 'if_octets', 'if_packets']

    for key in vm_instance:
        instance = ''
        cpu_num = ''
        memory = ''
        disks = []
        net_interfaces = []

        for sub_key in vm_instance[key]:
            if sub_key == 'name':
                instance = vm_instance[key][sub_key]
            if sub_key == 'cpu_num':
                cpu_num = vm_instance[key][sub_key]
            if sub_key == 'memory':
                memory = vm_instance[key][sub_key]
            if sub_key == 'disks':
                disks = vm_instance[key][sub_key].split()
            if sub_key == 'net_interfaces':
                net_interfaces = vm_instance[key][sub_key].split()

        # Insert vcpu data
        val = collectd.Values(host=instance, plugin='virt', plugin_instance=instance, type='virt_cpu_total')
        values = random.randint(0, CPU_MAX_VALUE) 
        val.dispatch(values=[values])

        for i in range(0, int(cpu_num)):
            val = collectd.Values(host=instance, plugin='virt', plugin_instance=instance, type='virt_vcpu', type_instance=str(i))
            values = random.randint(0, VCPU_MAX_VALUE) 
            val.dispatch(values=[values])

        # Insert vmem data
        for temp_instance in virt_memory_type:
            val = collectd.Values(host=instance, plugin='virt', plugin_instance=instance, type='memory', type_instance=temp_instance)
            if temp_instance == 'total' or temp_instance == 'available':
                values = int(memory)*1024*1024
            elif temp_instance == 'unused':
                values = int(memory)*1024*1024 - 10485760
            elif temp_instance == 'swap_in' or temp_instance == 'swap_out':
                values = 0
            else:
                values = random.randint(0, int(memory)*1024*1024)
            val.dispatch(values=[values])

        # Insert vdisk data
        for i in disks:
            for temp_type in virt_disk_type:
                val = collectd.Values(host=instance, plugin='virt', plugin_instance=instance, type=temp_type, type_instance=str(i))
                if temp_type == 'disk_octets':
                    values_read = random.randint(0, MAX_VALUE*1024)
                    values_write = random.randint(0, MAX_VALUE*1024)
                elif temp_type == 'disk_ops':
                    values_read = random.randint(0, MAX_VALUE)
                    values_write = random.randint(0, MAX_VALUE)
                val.dispatch(values=[values_read, values_write])

        # Insert vnic data
        for i in net_interfaces:
            for temp_type in virt_net_type:
                val = collectd.Values(host=instance, plugin='virt', plugin_instance=instance, type=temp_type, type_instance=str(i))
                if temp_type == 'if_errors' or temp_type == 'if_dropped':
                    values_read = 0
                    values_write = 0
                elif temp_type == 'if_octets':
                    values_read = random.randint(0, MAX_VALUE*1024*1024)
                    values_write = random.randint(0, MAX_VALUE*1024*1024)
                elif temp_type == 'if_packets':
                    values_read = random.randint(0, MAX_VALUE)
                    values_write = random.randint(0, MAX_VALUE)

                val.dispatch(values=[values_read, values_write])

collectd.register_config(fake_virt_config)
collectd.register_read(fake_virt_read)
