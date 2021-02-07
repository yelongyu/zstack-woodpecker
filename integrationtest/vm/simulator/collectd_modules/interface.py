import collectd
import random

#MAX_VALUE = 9223372036854775807
MAX_VALUE = 100
net_interfaces = []
instance = ''

def fake_if_config(config):
    for node in config.children:
        key = node.key.lower()
        val = node.values[0]

        if key == 'instance':
            global instance
            instance = val
        elif key == 'net_interfaces':
            global net_interfaces
            net_interfaces = val.split()
        else:
            collectd.info('unknown config key %s for plugin interface' % key)

def fake_if_read():

    type_l = ['if_errors', 'if_octets', 'if_dropped', 'if_packets']

    for i in net_interfaces:
        for temp_type in type_l:
            val = collectd.Values(host=instance, plugin='interface', plugin_instance=str(i), type=temp_type)
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

collectd.register_config(fake_if_config)
collectd.register_read(fake_if_read)
