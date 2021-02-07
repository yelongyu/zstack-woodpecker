import collectd
import random

cpu_num = ''
instance = ''

def fake_cpu_config(config):
    for node in config.children:
        key = node.key.lower()
        val = node.values[0]

        if key == 'instance':
            global instance
            instance = val
        elif key == 'cpu_num':
            global cpu_num
            cpu_num = val
        else:
            collectd.info('unknown config key %s for plugin cpu' % key)

def fake_cpu_read():

    type_instance_l = ['idle', 'interrupt', 'nice', 'softirq', 'steal', 'system', 'user', 'wait']

    for i in range(0, int(cpu_num)):
        for temp_instance in type_instance_l:
            val = collectd.Values(host=instance, plugin='cpu', plugin_instance=str(i), type='percent', type_instance=temp_instance)
            values = random.uniform(0, 100)
            val.dispatch(values=[values])

collectd.register_config(fake_cpu_config)
collectd.register_read(fake_cpu_read)
