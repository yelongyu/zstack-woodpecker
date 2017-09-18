set -x
FILENAME=$1

LINENUMS=`grep -n '</*l2NoVlanNetwork' ${FILENAME} | awk -F ':' '{print $1}'`
echo ${LINENUMS}

for LN in ${LINENUMS}; do
	if [ "${START}" == "" -a "${END}" == "" ]; then
		START=${LN}
		continue
	fi

	END=${LN}
	echo ${START} ${END}
	sed -n ${START},${END}p ${FILENAME} | grep l3PublicNetworkName > /dev/null
	if [ $? -eq 0 ]; then
		sed  -i "${START},${END}s#provider=\"VirtualRouter\"#provider=\"Flat Network Service Provider\"#" ${FILENAME}
		sed  -i "${START},${END}s#provider=\"vrouter\"#provider=\"Flat Network Service Provider\"#" ${FILENAME}
		sed  -i "${START},${END}s#<serviceType>DNS</serviceType>#<serviceType>Userdata</serviceType>#" ${FILENAME}
#		sed  "${START},${END}s#provider="VirtualRouter"#provider="Flat Network Service Provider"#" ${FILENAME}
		echo found
	fi
	START=
	END=
done
