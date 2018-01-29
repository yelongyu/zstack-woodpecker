OS_CENTOS=7.2
cat /etc/redhat-release | grep '7.2' || OS_CENTOS=7.4
if [ "${OS_CENTOS}" == "7.2" ]; then
	bash -x `dirname $0`/setup_ceph_h_nodes.sh $@
else
	bash -x `dirname $0`/setup_ceph_j_nodes.sh $@
fi
