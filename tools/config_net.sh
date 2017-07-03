#/bin/bash
default_value=' '
ip=$default_value
netmask_default='255.255.255.0'
netmask=$default_value
gateway=$default_value
dns=$default_value
default_flag='1'
zsn0_flag=$default_flag
zsn1_flag=$default_flag
ifconfig zsn0 >/dev/null 2>&1 && zsn0_flag='0'
ifconfig zsn1 >/dev/null 2>&1 && zsn1_flag='0'
udev_file='/etc/udev/rules.d/70-persistent-net.rules'
zsn0_file='/etc/sysconfig/network-scripts/ifcfg-zsn0'
zsn1_file='/etc/sysconfig/network-scripts/ifcfg-zsn1'

help(){
    echo "Usage: $0 [Options]"
    echo "Change default network config from zsn1 to zsn0 with correct IP. If
not provide any Options. It will just change the zsn1 to zsn0, delete
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
    mv $zsn1_file $zsn0_file
    sed -i 's/NAME=zsn1/NAME=zsn0/' $zsn0_file
}

update_zsn0_ip(){
    sed -i '/BOOT/d' $zsn0_file
    sed -i '/IPADDR/d' $zsn0_file
    sed -i '/NETMASK/d' $zsn0_file
    sed -i '/GATEWAY/d' $zsn0_file
    sed -i '/HWADDR/d' $zsn0_file
    echo "BOOTPROTO=none" >> $zsn0_file
    echo "IPADDR=$ip" >> $zsn0_file
    echo "NETMASK=$netmask" >> $zsn0_file
    echo "GATEWAY=$gateway" >> $zsn0_file
    #echo "HWADDR=$mac" >> $zsn0_file
}

reboot_machine(){
    echo "$(tput bold) - Will reboot machine in 5 seconds ... [Ctrl-c] to cancel reboot and do it yourself. $(tput sgr0)"
    sleep 5
    reboot
}

if [ $ip = $default_value ] && [ ! $zsn0_flag = $default_flag ]; then
    echo "zsn0 device is alive and not provide specific IP to set. Quit..."
    exit
fi

if [ $ip = $default_value ] && [ $zsn0_flag = $default_flag ] && [ ! $zsn1_flag = $default_flag ]; then
    remove_udev_file
    mv_net_file
    echo "Has deleted $udev_file and move $zsn1_file to $zsn0_file"
    reboot_machine
fi

if [ ! $ip = $default_value ] && [ ! $zsn0_flag = $default_flag ]; then
    remove_udev_file
    update_zsn0_ip
    echo "Has deleted $udev_file and update zsn0 ip to $ip"
    ifconfig zsn0 $ip
fi

if [ ! $ip = $default_value ] && [ $zsn0_flag = $default_flag ] && [ ! $zsn1_flag = $default_flag ]; then
    remove_udev_file
    mv_net_file
    update_zsn0_ip
    echo "Has deleted $udev_file, move $zsn1_file to $zsn0_file and update zsn0 ip to $ip"
    reboot_machine
fi

