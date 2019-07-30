# coding=utf-8


zh_en = {
    u"创建": "create",
    u"停止": "stop",
    u"启动": "start",
    u"删除": "delete",
    u"彻底删除": "expunge",
    u"恢复": "recover",
    u"加载": "attach",
    u"卸载": "detach",
    u"迁移": "migrate",
    u"存储迁移": "ps_migrate",
    u"重置": "reinit",
    u"重启": "reboot",
    u"更换": "change",
    u"批量删除": "batch_delete",
    u"克隆": "clone",
    u"扩容": "resize",
    u"添加": "add",
    u"解绑": "detach",

    u"云主机": "vm",
    u"云主机镜像": "vm_image",
    u"云主机高可用": "ha",
    u"云主机从iso": "vm_from_iso",
    u"云主机从镜像": "vm_from_image",
    u"云主机从备份": "vm_from_backup",

    u"整机": "vm_with_volume",
    u"整机快照": "vm_snapshot",
    u"整机备份": "vm_backup",
    u"整机从整机备份": "vm_from_vmbackup",

    u"根云盘": "root_volume",
    u"根云盘快照": "root_snapshot",
    u"根云盘备份": "root_backup",

    u"数据云盘": "data_volume",
    u"云盘快照": "data_snapshot",
    u"云盘镜像": "data_image",
    u"云盘备份": "data_backup",
    u"云盘从镜像": "volume_from_image",
    u"云盘加载云主机": "volume_attached_vm",

    u"镜像": "image",
    u"iso": "iso",
    u"快照": "snapshot",
    u"镜像从云主机": "image_from_vm",
    u"镜像从云盘":"image_from_volume",
    u"镜像从备份" : "image_from_backup",
    u"镜像从快照": "image_from_snapshot",

    u"厚制备": "flag=thick",
    u"精简制备": "flag=thin",
    u"cpu随机": "'cpu=random'",
    u"memory随机": "'memory=random'",
    u"平台随机": "'platform=random'",
    u"网络随机": "'network=random'",
    u"容量随机": "'size=random'",
    u"带云盘": "'data_volume=true'",
    u"windows": "'flag=windows'",
    u"linux": "flag=linux",
    u"large": "flag=large",
    u"大": "flag=large",
    u"scsi": "flag=scsi",
    u"share": "flag=shareable",
    u'sblk': "flag=sblk",
    u'ceph': "flag=ceph"


}


def change_to_english(word_list):
    # 动作 资源 flag
    return zh_en[word_list[0]] + "_" + zh_en[word_list[1]], parse_tags(word_list[2:])


def parse_tags(arg_list):
    args = []
    flag = []
    if arg_list:
        for i in arg_list:
            if "flag" in zh_en[i]:
                flag.append(zh_en[i].split("=")[1])
                continue
            args.append(zh_en[i])
    if flag:
        args.append("'flag=" + ",".join(flag) + "'")
    return args


if __name__ == "__main__":
    print change_to_english([u"创建", u"数据云盘", u"容量随机"])
