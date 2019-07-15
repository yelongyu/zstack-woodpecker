```bash
$ pip install jieba

$ python trans.py -h
Usage: translation robot path

Options:
  -h, --help            show this help message and exit
  -f CSV_FILE, --file=CSV_FILE
                        PICT tool exports a csv file
  -r DIRECTORY, --directory=DIRECTORY
                        [Optional]The auto created path file will be put in
                        this directory. Default is current directory
  -n NUM, --num=NUM     [Optional]The auto created path file will be named
                        path[num].py. Defaule value is 1
  -m, --mini            [Optional]if env is mini must add -m
```

| 中文action名                    | tags             | robot action name        | Done |
| ------------------------------- | ---------------- | ------------------------ | ---- |
| 创建云主机                      | 厚制备           | create_vm/create_mini_vm | Done |
| 停止云主机                      | 精简制备         | stop_vm                  | Done |
| 删除云主机                      | cpu随机(mini)    | destroy_vm               | Done |
| 彻底删除云主机                  | memory随机(mini) | expunge_vm               | Done |
| 恢复云主机                      | 网络随机         | recover_vm               | Done |
| 重启云主机                      | 容量随机(mini)   | reboot_vm                | Done |
| 启动云主机                      | large/大(mini)   | start_vm                 | Done |
| 扩容云主机/扩容根云盘           | scsi             | resize_volume            | Done |
| 重置云主机                      | share            | reinit_vm                |      |
| 迁移云主机                      | 带云盘           | migrate_vm               |      |
| 存储迁移云主机                  |                  | ps_migrate_vm            |      |
| 更换云主机高可用                |                  | change_vm_ha             | Done |
| 克隆云主机                      |                  | clone_vm                 |      |
| 更换云主机镜像(Todo)            |                  |                          |      |
| 克隆整机                        |                  |                          |      |
|                                 |                  |                          |      |
|                                 |                  |                          |      |
| 创建数据云盘                    |                  | create_volume            | Done |
| 加载数据云盘                    |                  | attach_volume            | Done |
| 卸载数据云盘                    |                  | detach_volume            | Done |
| 删除数据云盘                    |                  | delete_volume            | Done |
| 彻底删除数据云盘                |                  | expunge_volume           | Done |
| 扩容数据云盘                    |                  | resize_data_volume       | Done |
| 恢复数据云盘                    |                  | recover_volume           | Done |
| 迁移数据云盘                    |                  | migrate_volume           |      |
| 存储迁移数据云盘                |                  | ps_migrate_volume        |      |
|                                 |                  |                          |      |
|                                 |                  |                          |      |
| 创建根云盘快照                  |                  | create_volume_snapshot   | Done |
| 创建整机快照                    |                  | create_vm_snapshot       | Done |
| 创建云盘快照                    |                  | create_volume_snapshot   | Done |
| 删除根云盘快照                  |                  | delete_volume_snapshot   | Done |
| 删除整机快照                    |                  | delete_vm_snapshot       | Done |
| 删除云盘快照                    |                  | delete_volume_snapshot   | Done |
| 恢复根云盘快照                  |                  | use_volume_snapshot      | Done |
| 恢复整机快照                    |                  | use_vm_snapshot          | Done |
| 恢复云盘快照                    |                  | use_volume_snapshpt      | Done |
| 批量删除快照                    |                  | batch_delete_snapshots   | Done |
| 解绑整机快照                    |                  | ungroup_vm_snaoshot      | Done |
|                                 |                  |                          |      |
|                                 |                  |                          |      |
| 创建根云盘备份                  |                  | create_volume_backup     | Done |
| 创建整机备份                    |                  | create_vm_backup         | Done |
| 创建云盘备份                    |                  | create_volume_backup     | Done |
| 删除根云盘备份                  |                  | delete_volume_backup     | Done |
| 删除整机备份                    |                  | delete_vm_backup         | Done |
| 删除云盘备份                    |                  | delete_volume_backup     | Done |
| 恢复根云盘备份                  |                  | use_volume_backup        | Done |
| 恢复整机备份                    |                  | use_vm_backup            | Done |
| 恢复云盘备份                    |                  | use_volume_backup        | Done |
| 创建整机从整机备份              |                  | create_vm_from_vmbackup  | Done |
|                                 |                  |                          |      |
|                                 |                  |                          |      |
| 添加镜像                        |                  | add_image                | Done |
| 添加iso                         |                  | add_iso                  | Done |
| 删除镜像                        |                  | delete_image             | Done |
| 恢复镜像                        |                  | recover_image            | Done |
| 彻底删除镜像                    |                  | expunge_image            | Done |
| 创建云主机从镜像                |                  | create_vm_by_image       |      |
| 创建云主机从iso                 |                  | create_vm_by_image       |      |
| 创建云盘从镜像                  |                  | create_volume_by_image   |      |
| 创建镜像从云主机/创建云主机镜像 |                  | create_image_from_volume |      |
| 创建镜像从云盘/创建云盘镜像     |                  |                          |      |
| 创建镜像从快照                  |                  |                          |      |
| 创建镜像从备份                  |                  |                          |      |
|                                 |                  |                          |      |
|                                 |                  |                          |      |
|                                 |                  |                          |      |
|                                 |                  |                          |      |
|                                 |                  |                          |      |
|                                 |                  |                          |      |
|                                 |                  |                          |      |
|                                 |                  |                          |      |
|                                 |                  |                          |      |
|                                 |                  |                          |      |