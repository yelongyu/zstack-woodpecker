#!/bin/bash

which jq &>/dev/null
[ $? -ne 0 ] && echo -e "\n\ninstall jq for parsing json\n\n" && yum install -y jq

for pool in `ceph osd lspools -f json|jq '.[]'|jq '.poolname'`; do
    poolname=`eval echo $pool`
    if [[ $poolname == pri* ]]; then
        echo "delete $poolname"
        ceph osd pool delete $poolname $poolname --yes-i-really-really-mean-it
    fi
    if [[ $poolname == bak* ]]; then
        echo "delete $poolname"
        ceph osd pool delete $poolname $poolname --yes-i-really-really-mean-it
    fi
done

echo -e "\n\nZStack's Pools have been cleaned up.\n\n"
