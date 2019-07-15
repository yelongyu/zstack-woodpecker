# encoding=utf-8

from action import *

fun_dict = {
    "create_vm": create_vm,
    "start_vm": start_vm,
    "stop_vm": stop_vm,
    "delete_vm": destroy_vm,
    "expunge_vm": expunge_vm,
    "recover_vm": recover_vm,
    "reinit_vm": reinit_vm,
    "migrate_vm": migrate_vm,
    "resize_vm": resize_root_volume,
    "ps_migrate_vm": ps_migrate_vm,
    "reboot_vm": reboot_vm,
    "change_vm_image": change_vm_image,
    "change_ha": change_vm_ha,
    #
    "clone_vm": clone_vm,
    "clone_vm_with_volume": clone_vm,
    #
    "resize_root_volume": resize_root_volume,
    "create_root_backup": create_root_backup,
    "recover_root_backup": use_root_backup,
    "delete_root_backup": delete_root_backup,
    #
    "create_root_snapshot": create_root_snapshot,
    "recover_root_snapshot": use_root_snapshot,
    "delete_root_snapshot": delete_root_snapshot,
    #
    "create_vm_backup": create_vm_backup,
    "recover_vm_backup": use_vm_backup,
    "delete_vm_backup": delete_vm_backup,
    "create_vm_snapshot": create_vm_snapshot,
    "recover_vm_snapshot": use_vm_snapshot,
    "delete_vm_snapshot": delete_vm_snapshot,
    "detach_vm_snapshot": detach_vm_snapshot,
    #
    "create_data_volume": create_volume,
    "delete_data_volume": delete_volume,
    "expunge_data_volume": expunge_volume,
    "recover_data_volume": recover_volume,
    "resize_data_volume": resize_volume,
    "attach_data_volume": attach_volume,
    "detach_data_volume": detach_volume,
    "migrate_data_volume": migrate_volume,
    "ps_migrate_data_volume": ps_migrate_volume,
    #
    "create_data_backup": create_volume_backup,
    "recover_data_backup": use_volume_backup,
    "delete_data_backup": delete_volume_backup,
    "create_data_snapshot": create_volume_snapshot,
    "recover_data_snapshot": use_volume_snapshot,
    "delete_data_snapshot": delete_volume_snapshot,
    #
    "add_image": add_image,
    # "add_data_image": add_data_image,
    "add_iso": add_iso,
    "delete_image": delete_image,
    "recover_image": recover_image,
    "expunge_image": expunge_image,
    # "export_image": export_image,
    "create_vm_image": create_image_from_vm,
    "create_data_image": create_image_from_volume,
    "create_image_from_snapshot": create_image_from_snapshot,
    "create_image_from_backup": create_image_from_backup,
    "create_image_from_vm": create_image_from_vm,
    "create_image_from_volume": create_image_from_volume,

    "create_vm_from_iso": create_vm_from_iso,
    "create_vm_from_image": create_vm_from_image,
    #"create_vm_from_backup": create_vm_from_backup,
    "create_vm_from_vmbackup": create_vm_from_vmbackup,
    "create_volume_from_image": create_volume_from_image,

    "batch_delete_snapshot": batch_delete_snapshots
    # "attach_iso": attach_iso,
    # "detach_iso": detach_iso,
}


def parse_path(path):
    action = path[0]
    tags = path[1]
    return fun_dict[action]().run(tags)

