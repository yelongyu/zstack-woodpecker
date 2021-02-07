import collectd
import random

memory = ''
instance = ''

def fake_mem_config(config):
    for node in config.children:
        key = node.key.lower()
        val = node.values[0]

        if key == 'instance':
            global instance
            instance = val
        elif key == 'memory':
            global memory
            memory = val
        else:
            collectd.info('unknown config key %s for plugin mem' % key)

def fake_mem_read():

    plugin_instance_l = ['used', 'buffered', 'cached', 'free', 'slab_recl', 'slab_unrecl']

    for temp_instance in plugin_instance_l:
        val = collectd.Values(host=instance, plugin='memory', plugin_instance=temp_instance, type='memory')
        if temp_instance == 'used':
            used_values = random.randint(0, (int(memory)/2)*1024*1024)
            val.dispatch(values=[used_values])
        elif temp_instance == 'free':
            free_values = int(memory)*1024*1024 - used_values
            val.dispatch(values=[free_values])
        else:
            values = 0
            val.dispatch(values=[values])
            

collectd.register_config(fake_mem_config)
collectd.register_read(fake_mem_read)
