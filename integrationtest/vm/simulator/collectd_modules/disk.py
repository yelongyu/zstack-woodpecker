import collectd
import random

#MAX_VALUE = 9223372036854775807
MAX_VALUE = 100
disk_instances = []
instance = ''

def fake_disk_config(config):
    for node in config.children:
        key = node.key.lower()
        val = node.values[0]

        if key == 'instance':
            global instance
            instance = val
        elif key == 'disk_instances':
            global disk_instances
            disk_instances = val.split()
        else:
            collectd.info('unknown config key %s for plugin disk' % key)

def fake_disk_read():

    type_l = ['disk_io_time', 'disk_merged', 'disk_octets', 'disk_ops', 'disk_time']

    for i in disk_instances:
        for temp_type in type_l:
            val = collectd.Values(host=instance, plugin='disk', plugin_instance=str(i), type=temp_type)
            if temp_type == 'disk_octets':
                values_read = random.randint(0, MAX_VALUE*1024)
                values_write = random.randint(0, MAX_VALUE*1024)
            elif temp_type == 'disk_ops':
                values_read = random.randint(0, MAX_VALUE)
                values_write = random.randint(0, MAX_VALUE)
            else:
                values_read = random.randint(0, MAX_VALUE*1024)
                values_write = random.randint(0, MAX_VALUE*1024)

            val.dispatch(values=[values_read, values_write])

collectd.register_config(fake_disk_config)
collectd.register_read(fake_disk_read)
