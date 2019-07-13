# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
from test_stub import *


class VOLUME(MINI):
    def __init__(self, uri=None, initialized=False):
        self.volume_name = None
        self.volume_list = []
        if initialized:
            # if initialized is True, uri should not be None
            self.uri = uri
            return
        super(VOLUME, self).__init__()

    def create_volume(self, name=None, dsc=None, size='2 GB', cluster=None, vm=None, provisioning=u'厚置备', view='card'):
        cluster = cluster if cluster else os.getenv('clusterName')
        self.volume_name = name if name else 'volume-' + get_time_postfix()
        self.volume_list.append(self.volume_name)
        test_util.test_logger('Create Volume [%s]' % self.volume_name)
        volume_dict = {'name': self.volume_name,
                       'description': dsc,
                       'dataSize': size.split(),
                       'clusterUuid': cluster,
                       'vmUuid': vm,
                       'provisioning': provisioning}
        volume_elem = self.create(volume_dict, "volume", view=view)
        checker = MINICHECKER(self, volume_elem)
        if vm:
            check_list = [self.volume_name, vm, size]
            checker.volume_check(check_list)
        else:
            check_list = [self.volume_name, size]
            checker.volume_check(check_list=check_list, ops='detached')

    def delete_volume(self, volume_name=None, view='card', corner_btn=True, details_page=False):
        volume_name = volume_name if volume_name else self.volume_list
        self.delete(volume_name, 'volume', view=view, corner_btn=corner_btn, details_page=details_page)

    def expunge_volume(self, volume_name=None, view='card', details_page=False):
        volume_name = volume_name if volume_name else self.volume_list
        self.delete(volume_name, 'volume', view=view, expunge=True, details_page=details_page)

    def volume_attach_to_vm(self, dest_vm, volume_name=[], details_page=False):
        emptyl = []
        volume_list = volume_name if volume_name != [] else self.volume_name
        if not isinstance(volume_list, types.ListType):
            emptyl.append(volume_list)
            volume_list = emptyl
        self.navigate('volume')
        self.more_operate(u'加载', res_type='volume', res_name=volume_list, details_page=details_page)
        for _row in self.get_elements(TABLEROW):
            if dest_vm in _row.text:
                break
        else:
            test_util.test_fail('Can not find the dest-vm with name [%s]' % dest_vm)
        _row.get_element('input[type="radio"]').click()
        self.click_ok()
        check_list = [dest_vm]
        for vol in volume_list:
            _elem = self.get_res_element(vol)
            MINICHECKER(self, _elem).volume_check(check_list)
            test_util.test_logger('[%s] attach to [%s] successfully' % (vol, dest_vm))

    def volume_detach_from_vm(self, volume_name=[], details_page=False):
        emptyl = []
        volume_list = volume_name if volume_name != [] else self.volume_name
        if not isinstance(volume_list, types.ListType):
            emptyl.append(volume_list)
            volume_list = emptyl
        self.navigate('volume')
        self.more_operate(u'卸载', res_type='volume', res_name=volume_list, details_page=details_page)
        self.click_ok()
        for vol in volume_list:
            _elem = self.get_res_element(vol)
            MINICHECKER(self, _elem).volume_check(ops='detached')
            test_util.test_logger('[%s] detach from vm successfully' % vol)
