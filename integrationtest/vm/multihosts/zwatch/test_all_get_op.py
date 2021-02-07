'''
test all GetXXX api

@author: rhZhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.zwatch_operations as zwt_ops
import apibinding.inventory as inventory
import time

test_stub = test_lib.lib_get_test_stub()


def test():
    begin_time = int(round(time.time() * 1000))
    # test GetAllMetricmetadata and GetAllEventMetadata
    all_metric_metadata = zwt_ops.get_all_metric_metadata()
    test_util.test_dsc('total account of metric metadata:%s' % len(all_metric_metadata))
    all_event_metadata = zwt_ops.get_all_event_metadata()
    test_util.test_dsc('total account of event metadata:%s' % len(all_event_metadata))

    metric_metadata_with_label_list = []
    metric_metadata_without_label_list = []
    for metric_metadata in all_metric_metadata:
        if metric_metadata.labelNames:
            metric_metadata_with_label_list.append(metric_metadata)
        # test_util.test_dsc('\n[namespace]:%s [name]:%s [labelNames]:%s '%(metric_metadata.namespace,
        # metric_metadata.name,metric_metadata.labelNames))
        else:
            metric_metadata_without_label_list.append(metric_metadata)
        # test_util.test_dsc('\n[namespace]:%s [name]:%s '%(metric_metadata.namespace,metric_metadata.name))

    # test GetMetrciLabelValue
    for metric_metadata in metric_metadata_with_label_list:
        if len(metric_metadata.labelNames) == 1:
            labels = zwt_ops.get_metric_label_value(metric_metadata.namespace, metric_metadata.name,
                                                      metric_metadata.labelNames)
        # test_util.test_dsc('%s metric metadata only has one label:'%metric_metadata.name)
        # for label in labels:
        # test_util.test_logger(' [%s] : %s\n'%(metric_metadata.labelNames[0],label[metric_metadata.labelNames[0]]))
        if len(metric_metadata.labelNames) == 2:
            labels = zwt_ops.get_metric_label_value(metric_metadata.namespace, metric_metadata.name,
                                                      metric_metadata.labelNames)
        # test_util.test_dsc('%s metric metadata has two labels:'%metric_metadata.name)
        # for label in labels:
        # 	test_util.test_logger(' [%s] : %s\n [%s]: %s\n'%(metric_metadata.labelNames[0],
    # label[metric_metadata.labelNames[0]],metric_metadata.labelNames[1],label[metric_metadata.labelNames[1]]))

    # test GetMetricData
    for metric_metadata in all_metric_metadata:
        data_list = zwt_ops.get_metric_data(metric_metadata.namespace, metric_metadata.name)
    # for data in data_list:
    # 	test_util.test_logger('%s:[labels]:%s [time]:%s [value]:%s'%(metric_metadata.name,data.labels,data.time,
    # data.value))

    # test PutMetricData
    my_namespace = 'MyNamespace'
    my_metric_name = 'MySQLMaxConnections'
    my_labels = {"ip": "10.0.0.10"}
    my_data = [{"metricName": my_metric_name, "value": 1000, "labels": my_labels}]
    zwt_ops.put_metric_data(my_namespace, my_data)

    # wait for data
    time.sleep(60)
    my_data_get = zwt_ops.get_metric_data(my_namespace, my_metric_name)
    if not my_data_get:
        test_util.test_fail('put metric data %s failed' % my_metric_name)

    # test GetEventData
    events = zwt_ops.get_event_data()
    zwt_ops.get_alarm_data()
    # if events:
    # 	test_util.test_dsc('all events happend are list as below:\n')
    # 	for event in events:
    # 		test_util.test_logger('[time]:%s,[namespace]:%s ,[name]:%s,[labels]:%s,[resourceId]:%s'%(event.time,
    # event.namespace,event.name,event.labels,event.resourceId))

    # test GetAuditData
    current_time = int(round(time.time() * 1000))
    audits = zwt_ops.get_audit_data(start_time=begin_time, end_time=current_time)
    flag = 0
    for audit_data in audits:
        if inventory.APIPUTMETRICDATAMSG_FULL_NAME == audit_data.apiName:
            flag = 1
    if not flag:
        test_util.test_fail('can\'nt get last audit data:%s' % inventory.APIPUTMETRICDATAMSG_FULL_NAME)

    test_util.test_pass('success test all GetXXX api!')


# Will be called only if exception happens in test().
def error_cleanup():
    pass
