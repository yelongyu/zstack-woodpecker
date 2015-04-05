#/bin/bash
default_value=' '
ip=$default_value
netmask_default='255.255.255.0'
netmask=$default_value
gateway=$default_value
dns=$default_value
default_flag='1'
eth0_flag=$default_flag
eth1_flag=$default_flag
ifconfig eth0 >/dev/null 2>&1 && eth0_flag='0'
ifconfig eth1 >/dev/null 2>&1 && eth1_flag='0'
udev_file='/etc/udev/rules.d/70-persistent-net.rules'
eth0_file='/etc/sysconfig/network-scripts/ifcfg-eth0'
eth1_file='/etc/sysconfig/network-scripts/ifcfg-eth1'

help(){
    echo "Usage: $0 [Options]"
    echo "Change default network config from eth1 to eth0 with correct IP. If
not provide any Options. It will just change the eth1 to eth0, delete
/etc/udev/rules.d/70-persistent-net.rules and reboot the system."
    echo "
[Options:]
	-i IP_ADDR	[Optional] new IP Address. Default: DHCP
	-n NETMASK	[Optional] netmask . Default: $netmask_default
	-g GATWAY	[Optional]  
	-d DNS		[Optional]
	-h		[Optional] show this message and exit.
"
    exit 1
}

OPTIND=1
while getopts "i:n:g:d:h" Option
do
    case $Option in
        i ) ip=$OPTARG;;
        n ) netmask=$OPTARG;;
        g ) gateway=$OPTARG;;
        d ) dns=$OPTARG;;
        h ) help;;
        * ) help;;
    esac
done
OPTIND=1

remove_udev_file(){
    rm -f $udev_file || echo "$udev_file does not exist"
}

mv_net_file(){
    mv $eth1_file $eth0_file
    sed -i 's/NAME=eth1/NAME=eth0/' $eth0_file
}

update_eth0_ip(){
    sed -i '/BOOT/d' $eth0_file
    sed -i '/IPADDR/d' $eth0_file
    sed -i '/NETMASK/d' $eth0_file
    sed -i '/GATEWAY/d' $eth0_file
    sed -i '/HWADDR/d' $eth0_file
    echo "BOOTPROTO=none" >> $eth0_file
    echo "IPADDR=$ip" >> $eth0_file
    echo "NETMASK=$netmask" >> $eth0_file
    echo "GATEWAY=$gateway" >> $eth0_file
    #echo "HWADDR=$mac" >> $eth0_file
}

reboot_machine(){
    echo "$(tput bold) - Will reboot machine in 5 seconds ... [Ctrl-c] to cancel reboot and do it yourself. $(tput sgr0)"
    sleep 5
    reboot
}

if [ $ip = $default_value ] && [ ! $eth0_flag = $default_flag ]; then
    echo "eth0 device is alive and not provide specific IP to set. Quit..."
    exit
fi

if [ $ip = $default_value ] && [ $eth0_flag = $default_flag ] && [ ! $eth1_flag = $default_flag ]; then
    remove_udev_file
    mv_net_file
    echo "Has deleted $udev_file and move $eth1_file to $eth0_file"
    reboot_machine
fi

if [ ! $ip = $default_value ] && [ ! $eth0_flag = $default_flag ]; then
    remove_udev_file
    update_eth0_ip
    echo "Has deleted $udev_file and update eth0 ip to $ip"
    ifconfig eth0 $ip
fi

if [ ! $ip = $default_value ] && [ $eth0_flag = $default_flag ] && [ ! $eth1_flag = $default_flag ]; then
    remove_udev_file
    mv_net_file
    update_eth0_ip
    echo "Has deleted $udev_file, move $eth1_file to $eth0_file and update eth0 ip to $ip"
    reboot_machine
fi

