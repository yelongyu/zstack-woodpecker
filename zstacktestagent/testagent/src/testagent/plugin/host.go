package plugin

import (
	"testagent/server"
	"testagent/utils"
	"fmt"
	"strings"
)


type HostDeleteBridgeCmd struct {
	BridgeName string `json:"bridge_name"`
}

type HostShellCmd struct {
	Command string `json:"command"`
}

type HostShellRsp struct {
	ReturnCode int `json:"return_code"`
	Stderr string `json:"stderr"`
	Stdout string `json:"stdout"`
	Command string `json:"command"`
	Success bool `json:"success"`
}

type HostCreateVlanDeviceCmd struct {
	Ethname string `json:"ethname"`
	Vlan int `json:"vlan"`
	Ip_ string `json:"ip_"`
	Netmask_ string `json:"netmask_"`
}

type HostDeleteVlanDeviceCmd struct {
	VlanEthname string `json:"vlan_ethname"`
}

type HostSetDeviceIpCmd struct {
	Ethname string `json:"ethname"`
	Ip string `json:"ip"`
	Netmask string `json:"netmask"`
}

type HostFlushDeviceIpCmd struct {
	Ethname string `json:"ethname"`
}

const (
	CREATE_VLAN_DEVICE_PATH = "/host/createvlandevice"
	DELETE_VLAN_DEVICE_PATH = "/host/deletevlandevice"
	DELETE_BRIDGE_PATH = "/host/deletebridgedevice"
	SET_DEVICE_IP_PATH = "/host/setdeviceip"
	FLUSH_DEVICE_IP_PATH = "/host/flushdeviceip"
	HOST_SHELL_CMD_PATH = "/host/shellcmd"
	HOST_VYOS_CMD_PATH = "/host/vyoscmd"
//	HOST_ECHO_PATH = "/host/echo"
)


func hostEchoHandler(ctx *server.CommandContext) interface{} {
	return nil
}

func DeleteVlanEth(VlanDevName string) {
	if isNetworkDeviceExisting(VlanDevName) {
		b := utils.NewBash()
		b.Command = fmt.Sprintf("ip link set dev %s down", VlanDevName)
		b.Run()

		b.Command = fmt.Sprintf("vconfig rem %s", VlanDevName)
		b.Run()
	}
}

func hostCreateVlanDeviceHandler(ctx *server.CommandContext) interface{} {
	b := utils.NewBash()
	cmd := &HostCreateVlanDeviceCmd{}
	ctx.GetCommand(cmd)

	if isNetworkDeviceExisting(cmd.Ethname) {
		VlanDevName := fmt.Sprintf("%s.%s", cmd.Ethname, cmd.Vlan)
		if !isNetworkDeviceExisting(VlanDevName) {
			b.Command = fmt.Sprintf("vconfig add %s %s", cmd.Ethname, strconv.Itoa(cmd.Vlan))
			b.Run()
			if cmd.Ip_ != "" {
				b.Command = fmt.Sprintf("ifconfig %s %s netmask %s", cmd.Ethname, VlanDevName, cmd.Netmask_)
				b.Run()
			}
		} else {
			if GetDeviceIp(VlanDevName) != cmd.Ip_ {
				DeleteVlanEth(VlanDevName)
				b.Command = fmt.Sprintf("vconfig add %s %s", cmd.Ethname, strconv.Itoa(cmd.Vlan))
				b.Run()
				b.Command = fmt.Sprintf("ifconfig %s %s netmask %s", VlanDevName, cmd.Ip_, cmd.Netmask_)
				b.Run()
			}
		}
	}
		
	return nil
}


func hostDeleteVlanDeviceHandler(ctx *server.CommandContext) interface{} {
	cmd := &HostDeleteVlanDeviceCmd{}
	ctx.GetCommand(cmd)

	DeleteVlanEth(cmd.VlanEthname)

	return nil
}

func GetAllBridgeInterface(bridgeName string) []string {
	bash := utils.Bash{
		Command: fmt.Sprintf("brctl show %s|sed -n '2,$p'|cut -f 6-10", bridgeName),
		NoLog: true,
	}
	_, out, _, _ := bash.RunWithReturn()
	vifs := strings.Split(out, "\n")
	for i, vif := range(vifs) {
		vifs[i] = strings.TrimSpace(vif)
	}
	return vifs
}

func hostDeleteBridgeHandler(ctx *server.CommandContext) interface{} {
	b := utils.NewBash()
	cmd := &HostDeleteBridgeCmd{}
	ctx.GetCommand(cmd)

	vifs := GetAllBridgeInterface(cmd.BridgeName)
	for _, vif := range(vifs) {
		b.Command = fmt.Sprintf("brctl delif %s %s", cmd.BridgeName, vif)
		b.Run()
	}

	b.Command = fmt.Sprintf("ip link set %s down", cmd.BridgeName)
	b.Run()

	b.Command = fmt.Sprintf("brctl delbr %s", cmd.BridgeName)
	b.Run()

	return nil
}


func GetDeviceIp(ethname string) string {
	bash := utils.Bash{
		Command: fmt.Sprintf("ip addr show dev %s|grep inet|grep -v inet6|awk -F'inet' '{print $2}'|awk '{print $1}'|awk -F'/24' '{print $1}'", ethname),
		NoLog: true,
	}
	_, out, _, err := bash.RunWithReturn()
	if err != nil {
		return ""
	} else {
		return out
	}
}

func hostSetDeviceIpHandler(ctx *server.CommandContext) interface{} {
	b := utils.NewBash()
	cmd := &HostSetDeviceIpCmd{}
	ctx.GetCommand(cmd)

	if isNetworkDeviceExisting(cmd.Ethname) {
		if GetDeviceIp(cmd.Ethname) != cmd.Ip {
			b.Command = fmt.Sprintf("ifconfig %s %s netmask %s", cmd.Ethname, cmd.Ip, cmd.Netmask)
			b.Run()
		}
	}

	return nil
}


func isNetworkDeviceExisting(ethname string) bool {
	bash := utils.Bash{
		Command: fmt.Sprintf("ip link show %s", ethname),
		NoLog: true,
	}
	returnCode, _, _, _ := bash.RunWithReturn()
	if returnCode == 0 {
		return true
	} else {
		return false
	}
}

func hostFlushDeviceIpHandler(ctx *server.CommandContext) interface{} {
	b := utils.NewBash()
	cmd := &HostFlushDeviceIpCmd{}
	ctx.GetCommand(cmd)

	if isNetworkDeviceExisting(cmd.Ethname) {
		b.Command = fmt.Sprintf("ip addr flush dev %s", cmd.Ethname)
		b.Run()
	}

	return nil
}


func hostShellCmdHandler(ctx *server.CommandContext) interface{} {
	cmd := &HostShellCmd{}
	ctx.GetCommand(cmd)
	var rsp HostShellRsp
	bash := utils.Bash{
		Command: cmd.Command,
		NoLog: true,
	}

	rsp.ReturnCode, rsp.Stdout, rsp.Stderr, _ = bash.RunWithReturn()
//	bash.PanicIfError()
	rsp.Command = cmd.Command
	rsp.Success = true

	return rsp
}

func hostVyosCmdHandler(ctx *server.CommandContext) interface{} {
	cmd := &HostShellCmd{}
	ctx.GetCommand(cmd)
	var rsp HostShellRsp

	rsp.Stdout = server.RunVyosScriptAsUserVyos(cmd.Command)
	rsp.Stderr = ""
	rsp.ReturnCode = 0
	rsp.Command = cmd.Command
	rsp.Success = true

	return rsp
}

func HostEntryPoint() {
	server.RegisterSyncCommandHandler(CREATE_VLAN_DEVICE_PATH, hostCreateVlanDeviceHandler)
	server.RegisterSyncCommandHandler(DELETE_VLAN_DEVICE_PATH, hostDeleteVlanDeviceHandler)
	server.RegisterSyncCommandHandler(DELETE_BRIDGE_PATH, hostDeleteBridgeHandler)
	server.RegisterSyncCommandHandler(SET_DEVICE_IP_PATH, hostSetDeviceIpHandler)
	server.RegisterSyncCommandHandler(FLUSH_DEVICE_IP_PATH, hostFlushDeviceIpHandler)
	server.RegisterSyncCommandHandler(HOST_SHELL_CMD_PATH, hostShellCmdHandler)
	server.RegisterSyncCommandHandler(HOST_VYOS_CMD_PATH, hostVyosCmdHandler)
//	server.RegisterSyncCommandHandler(HOST_ECHO_PATH, hostEchoHandler)
}
