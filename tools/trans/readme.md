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

| 中文action名                    | tags       | robot action name        | Done |
| ------------------------------- | ---------- | ------------------------ | ---- |
| 创建云主机                      | 厚制备     | create_vm/create_mini_vm |      |
| 停止云主机                      | 精简制备   | stop_vm                  |      |
| 删除云主机                      | cpu随机    | destroy_vm               |      |
| 彻底删除云主机                  | memory随机 | expunge_vm               |      |
| 恢复云主机                      | 网络随机   | recover_vm               |      |
| 重启云主机                      | 容量随机   | reboot_vm                |      |
| 启动云主机                      | large/大   | start_vm                 |      |
| 扩容云主机/扩容根云盘           | scsi       | resize_volume            |      |
| 重置云主机                      | share      | reinit_vm                |      |
| 迁移云主机                      | 带云盘     | migrate_vm               |      |
| 存储迁移云主机                  |            | ps_migrate_vm            |      |
| 更换云主机高可用                |            | change_vm_ha             |      |
| 克隆云主机                      |            | clone_vm                 |      |
| 更换云主机镜像(Todo)            |            |                          |      |
| 克隆整机                        |            |                          |      |
|                                 |            |                          |      |
|                                 |            |                          |      |
| 创建数据云盘                    |            | create_volume            |      |
| 加载数据云盘                    |            | attach_volume            |      |
| 卸载数据云盘                    |            | detach_volume            |      |
| 删除数据云盘                    |            | delete_volume            |      |
| 彻底删除数据云盘                |            | expunge_volume           |      |
| 扩容数据云盘                    |            | resize_data_volume       |      |
| 恢复数据云盘                    |            | recover_volume           |      |
| 迁移数据云盘                    |            | migrate_volume           |      |
| 存储迁移数据云盘                |            | ps_migrate_volume        |      |
|                                 |            |                          |      |
|                                 |            |                          |      |
| 创建根云盘快照                  |            | create_volume_snapshot   |      |
| 创建整机快照                    |            | create_vm_snapshot       |      |
| 创建云盘快照                    |            | create_volume_snapshot   |      |
| 删除根云盘快照                  |            | delete_volume_snapshot   |      |
| 删除整机快照                    |            | delete_vm_snapshot       |      |
| 删除云盘快照                    |            | delete_volume_snapshot   |      |
| 恢复根云盘快照                  |            | use_volume_snapshot      |      |
| 恢复整机快照                    |            | use_vm_snapshot          |      |
| 恢复云盘快照                    |            | use_volume_snapshpt      |      |
| 批量删除快照                    |            | batch_delete_snapshots   |      |
|                                 |            |                          |      |
|                                 |            |                          |      |
| 创建根云盘备份                  |            | create_volume_backup     |      |
| 创建整机备份                    |            | create_vm_backup         |      |
| 创建云盘备份                    |            | create_volume_backup     |      |
| 删除根云盘备份                  |            | delete_volume_backup     |      |
| 删除整机备份                    |            | delete_vm_backup         |      |
| 删除云盘备份                    |            | delete_volume_backup     |      |
| 恢复根云盘备份                  |            | use_volume_backup        |      |
| 恢复整机备份                    |            | use_vm_backup            |      |
| 恢复云盘备份                    |            | use_volume_backup        |      |
| 创建整机从整机备份              |            | create_vm_from_vmbackup  |      |
|                                 |            |                          |      |
|                                 |            |                          |      |
| 添加镜像                        |            | add_image                |      |
| 添加iso                         |            | add_iso                  |      |
| 删除镜像                        |            | delete_image             |      |
| 恢复镜像                        |            | recover_image            |      |
| 彻底删除镜像                    |            | expunge_image            |      |
| 创建云主机从镜像                |            | create_vm_by_image       |      |
| 创建云主机从iso                 |            | create_vm_by_image       |      |
| 创建云盘从镜像                  |            | create_volume_by_image   |      |
| 创建镜像从云主机/创建云主机镜像 |            | create_image_from_volume |      |
| 创建镜像从云盘/创建云盘镜像     |            |                          |      |
| 创建镜像从快照                  |            |                          |      |
| 创建镜像从备份                  |            |                          |      |
|                                 |            |                          |      |
|                                 |            |                          |      |
|                                 |            |                          |      |
|                                 |            |                          |      |
|                                 |            |                          |      |
|                                 |            |                          |      |
|                                 |            |                          |      |
|                                 |            |                          |      |
|                                 |            |                          |      |
|                                 |            |                          |      |