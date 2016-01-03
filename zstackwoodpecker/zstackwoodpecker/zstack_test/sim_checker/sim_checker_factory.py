'''
Zstack KVM Checker Factory.        


@author: YYK                   
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.volume as volume_header
import zstackwoodpecker.header.image as image_header
import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.zstack_test.zstack_checker.zstack_db_checker as db_checker
import zstackwoodpecker.test_util as test_util
import apibinding.inventory as inventory

class SimVmCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj): 
        sim_vm_checker_chain = checker_header.CheckerChain()
        checker_dict = {}

        if test_obj.state == vm_header.RUNNING:
            checker_dict[db_checker.zstack_vm_db_checker] = True
        elif test_obj.state == vm_header.STOPPED:
            checker_dict[db_checker.zstack_vm_db_checker] = True
        elif test_obj.state == vm_header.DESTROYED:
            checker_dict[db_checker.zstack_vm_db_checker] = True
        elif test_obj.state == vm_header.EXPUNGED:
            checker_dict[db_checker.zstack_vm_db_checker] = False

        sim_vm_checker_chain.add_checker_dict(checker_dict, test_obj)
        test_util.test_logger('Add checker: %s for [vm:] %s' % (sim_vm_checker_chain, test_obj.vm.uuid))
        return sim_vm_checker_chain

class SimVolumeCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj): 
        sim_volume_checker_chain = checker_header.CheckerChain()
        checker_dict = {}
        if test_obj.state == volume_header.CREATED:
            checker_dict[db_checker.zstack_volume_db_checker] = True
        elif test_obj.state == volume_header.ATTACHED:
            checker_dict[db_checker.zstack_volume_db_checker] = True
            if not test_obj.target_vm.state == vm_header.DESTROYED:
                checker_dict[db_checker.zstack_volume_attach_db_checker] = True
            else:
                checker_dict[db_checker.zstack_volume_attach_db_checker] = False

        elif test_obj.state == volume_header.DETACHED:
            checker_dict[db_checker.zstack_volume_db_checker] = True
            checker_dict[db_checker.zstack_volume_attach_db_checker] = False

        elif test_obj.state == volume_header.DELETED:
            checker_dict[db_checker.zstack_volume_db_checker] = True

        elif test_obj.state == volume_header.EXPUNGED:
            checker_dict[db_checker.zstack_volume_db_checker] = False

        sim_volume_checker_chain.add_checker_dict(checker_dict, test_obj)
        test_util.test_logger('Add checker: %s for [volume:] %s' % (sim_volume_checker_chain, test_obj.volume.uuid))
        return sim_volume_checker_chain

class SimImageCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj): 
        sim_image_checker_chain = checker_header.CheckerChain()
        checker_dict = {}
        if test_obj.state == image_header.CREATED:
            checker_dict[db_checker.zstack_image_db_checker] = True

        if test_obj.state == image_header.DELETED:
            #Image db will not deleted, as it might be used by some alive VMs.
            #checker_dict[db_checker.zstack_image_db_checker] = False
            pass
        sim_image_checker_chain.add_checker_dict(checker_dict, test_obj)
        test_util.test_logger('Add checker: %s for [image:] %s' % (sim_image_checker_chain, test_obj.image.uuid))
        return sim_image_checker_chain

