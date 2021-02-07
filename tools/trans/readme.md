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
  -p PATH_NAME, --path-name=PATH_NAME
                        [Optional]The auto created path file will named
                        {path_name}path[num].py
  -n NUM, --num=NUM     [Optional]The auto created path file will be named
                        path[num].py. Default value is 1
  -m, --mini            [Optional]if env is mini must add -m
  -l, --local           [Optional]if env is local must add -l
  -C CHECKING_POINT, --checking-point=CHECKING_POINT
                        [Optional]robot run checker until the step ==
                        checking-point. Default value is 1
  -F FAILD_POINT, --faild-point=FAILD_POINT
                        [Optional]robot run faild will return success when the
                        path-step == faild-point. Default value is 100000. If
                        you choose 'auto' ,that means the final step is faild-
                        point

```

| 中文action名                    | tags(创建云主机/云盘可选参数 直接跟在中文action名后如:创建云主机cephscsi) | robot action name        | Done |
| ------------------------------- | ------------------------------------------------------------ | ------------------------ | ---- |
| 创建云主机                      | 厚制备                                                       | create_vm/create_mini_vm | Done |
| 停止云主机                      | 精简制备                                                     | stop_vm                  | Done |
| 删除云主机                      | cpu随机          (mini vm)                                   | destroy_vm               |      |
| 彻底删除云主机                  | memory随机  (mini vm)                                        | expunge_vm               |      |
| 恢复云主机                      | 网络随机        (mini vm)                                    | recover_vm               |      |
| 重启云主机                      | 容量随机      (mini volume)                                  | reboot_vm                |      |
| 启动云主机                      | large/大        (mini volume)                                | start_vm                 |      |
| 扩容云主机/扩容根云盘           | scsi                                                         | resize_volume            |      |
| 重置云主机                      | share                                                        | reinit_vm                |      |
| 迁移云主机                      | 带云盘           (mini vm)                                   | migrate_vm               |      |
| 存储迁移云主机                  | cluster1        (mini vm/volume)                             | ps_migrate_vm            |      |
| 更换云主机高可用                | cluster2         (mini vm/volumr)                            | change_vm_ha             |      |
| 克隆云主机                      |                                                              | clone_vm                 |      |
| 更换云主机镜像(Todo)            |                                                              |                          |      |
| 克隆整机                        |                                                              |                          |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |
| 创建数据云盘                    |                                                              | create_volume            |      |
| 加载数据云盘                    |                                                              | attach_volume            |      |
| 卸载数据云盘                    |                                                              | detach_volume            |      |
| 删除数据云盘                    |                                                              | delete_volume            |      |
| 彻底删除数据云盘                |                                                              | expunge_volume           |      |
| 扩容数据云盘                    |                                                              | resize_data_volume       |      |
| 恢复数据云盘                    |                                                              | recover_volume           |      |
| 迁移数据云盘                    |                                                              | migrate_volume           |      |
| 存储迁移数据云盘                |                                                              | ps_migrate_volume        |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |
| 创建根云盘快照                  |                                                              | create_volume_snapshot   |      |
| 创建整机快照                    |                                                              | create_vm_snapshot       |      |
| 创建云盘快照                    |                                                              | create_volume_snapshot   |      |
| 删除根云盘快照                  |                                                              | delete_volume_snapshot   |      |
| 删除整机快照                    |                                                              | delete_vm_snapshot       |      |
| 删除云盘快照                    |                                                              | delete_volume_snapshot   |      |
| 恢复根云盘快照                  |                                                              | use_volume_snapshot      |      |
| 恢复整机快照                    |                                                              | use_vm_snapshot          |      |
| 恢复云盘快照                    |                                                              | use_volume_snapshpt      |      |
| 批量删除快照                    |                                                              | batch_delete_snapshots   |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |
| 创建根云盘备份                  |                                                              | create_volume_backup     |      |
| 创建整机备份                    |                                                              | create_vm_backup         |      |
| 创建云盘备份                    |                                                              | create_volume_backup     |      |
| 删除根云盘备份                  |                                                              | delete_volume_backup     |      |
| 删除整机备份                    |                                                              | delete_vm_backup         |      |
| 删除云盘备份                    |                                                              | delete_volume_backup     |      |
| 恢复根云盘备份                  |                                                              | use_volume_backup        |      |
| 恢复整机备份                    |                                                              | use_vm_backup            |      |
| 恢复云盘备份                    |                                                              | use_volume_backup        |      |
| 创建整机从整机备份              |                                                              | create_vm_from_vmbackup  |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |
| 添加镜像                        |                                                              | add_image                |      |
| 添加iso                         |                                                              | add_iso                  |      |
| 删除镜像                        |                                                              | delete_image             |      |
| 恢复镜像                        |                                                              | recover_image            |      |
| 彻底删除镜像                    |                                                              | expunge_image            |      |
| 创建云主机从镜像                |                                                              | create_vm_by_image       |      |
| 创建云主机从iso                 |                                                              | create_vm_by_image       |      |
| 创建云盘从镜像                  |                                                              | create_volume_by_image   |      |
| 创建镜像从云主机/创建云主机镜像 |                                                              | create_image_from_volume |      |
| 创建镜像从云盘/创建云盘镜像     |                                                              |                          |      |
| 创建镜像从快照                  |                                                              |                          |      |
| 创建镜像从备份                  |                                                              |                          |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |
|                                 |                                                              |                          |      |