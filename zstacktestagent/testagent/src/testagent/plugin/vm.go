package plugin

import (
	"fmt"
	"strings"
	"testagent/server"
	"testagent/utils"
	"time"
)

type VmStatusCheckCmd struct {
	Uuids []string `json:"vm_uuids"`
}

type VmDiskQosCmd struct {
	Uuid string `json:"vm_uuid"`
	Dev  string `json:"dev"`
}

type VmSshGuestVmCmd struct {
	Ip       string `json:"ip"`
	Command  string `json:"command"`
	Username string `json:"username"`
	Password string `json:"password"`
	Timeout  int    `json:"timeout"`
}

type VmSshGuestVmRsp struct {
	Success bool   `json:"success"`
	Error   string `json:"error"`
	Result  string `json:"result"`
}

type VmScpGuestVmCmd struct {
	Ip       string `json:"ip"`
	Username string `json:"username"`
	Password string `json:"password"`
	SrcFile  string `json:"src_file"`
	DstFile  string `json:"dst_file"`
	Timeout  int    `json:"timeout"`
}

type VmScpGuestVmRsp struct {
	Success bool   `json:"success"`
	Error   string `json:"error"`
}

type VmDiskQosRsp struct {
	VmDeviceIo string `json:"vm_device_io"`
}

type VmStatusCheckRsp struct {
	Vm_status map[string]bool `json:"vm_status"`
}

type VmStatusRsp struct {
	Vm_status map[string]string `json:"vm_status"`
}

type VmListAllVmRsp struct {
	Vm_status map[string][]string `json:"vm_status"`
}

type VmBlkStatusRsp struct {
	Vm_status map[string]map[string]string `json:"vm_status"`
}

const (
	IS_VM_STOPPED_PATH   = "/vm/isvmstopped"
	IS_VM_PAUSED_PATH    = "/vm/isvmpaused"
	IS_VM_DESTROYED_PATH = "/vm/isvmdestroyed"
	IS_VM_RUNNING_PATH   = "/vm/isvmrunning"
	SSH_GUEST_VM_PATH    = "/vm/sshguestvm"
	SCP_GUEST_VM_PATH    = "/vm/scpguestvm"
	VM_STATUS            = "/vm/vmstatus"
	LIST_ALL_VM          = "/vm/listallvm"
	VM_BLK_STATUS        = "/vm/vmblkstatus"
	VM_ECHO_PATH         = "/host/echo"
	VM_DEVICE_QOS        = "/vm/deviceqos"
)

const (
	VM_STATUS_RUNNING   = "running"
	VM_STATUS_STOPPED   = "shut off"
	VM_STATUS_PAUSED    = "paused"
	VM_STATUS_DESTROYED = ""
	VM_EXCEPTION_STATUS = "EXCEPTION_STATUS"
)

func isVmStatus(vm_uuid string, status string) bool {
	currentStatus := vmStatus(vm_uuid)
	fmt.Printf("%s\n", currentStatus)
	if currentStatus == status {
		return true
	} else {
		return false
	}
}

func vmStatus(vm_uuid string) string {
	bash := utils.Bash{
		Command: fmt.Sprintf("virsh domstate %s", vm_uuid),
		NoLog:   true,
	}

	retCode, o, _, err := bash.RunWithReturn()
	if err != nil || retCode != 0 {
		return VM_EXCEPTION_STATUS
	} else {
		return strings.TrimSpace(o)
	}
}

func vmSerialLog(vm_uuid string, status string) string {
	if status != VM_STATUS_RUNNING {
		_bash := utils.Bash{
			Command: fmt.Sprintf("rm -rf /tmp/%s_serial.log", vm_uuid),
			NoLog:   true,
		}

		_bash.Run()
		return VM_EXCEPTION_STATUS
	}

	bash_pts := utils.Bash{
		Command: fmt.Sprintf("grep pts /var/log/libvirt/qemu/%s.log | awk '{print $9}'", vm_uuid),
		NoLog:   true,
	}

	_retCode, _o, _, _err := bash_pts.RunWithReturn()
	if _err != nil || _retCode != 0 {
		return VM_EXCEPTION_STATUS
	} else {

		bash_serial_log := utils.Bash{
			Command: fmt.Sprintf("sh /tmp/serial_log_gen.sh %s_serial.log %s", vm_uuid, _o),
			NoLog:   true,
		}

		bash_serial_log.Run()
		return vm_uuid + "_serial.log"
	}
}

func vmIsVmStoppedHandler(ctx *server.CommandContext) interface{} {
	cmd := &VmStatusCheckCmd{}
	ctx.GetCommand(cmd)
	vm_status := make(map[string]bool)
	for _, uuid := range cmd.Uuids {
		vm_status[uuid] = isVmStatus(uuid, VM_STATUS_STOPPED)
	}

	return VmStatusCheckRsp{Vm_status: vm_status}
}

func vmIsVmSuspendedHandler(ctx *server.CommandContext) interface{} {
	cmd := &VmStatusCheckCmd{}
	ctx.GetCommand(cmd)
	vm_status := make(map[string]bool)
	for _, uuid := range cmd.Uuids {
		vm_status[uuid] = isVmStatus(uuid, VM_STATUS_PAUSED)
	}

	return VmStatusCheckRsp{Vm_status: vm_status}
}

func vmIsVmDestroyedHandler(ctx *server.CommandContext) interface{} {
	cmd := &VmStatusCheckCmd{}
	ctx.GetCommand(cmd)
	vm_status := make(map[string]bool)
	for _, uuid := range cmd.Uuids {
		vm_status[uuid] = isVmStatus(uuid, VM_STATUS_DESTROYED)
	}

	return VmStatusCheckRsp{Vm_status: vm_status}
}

func vmIsVmRunningHandler(ctx *server.CommandContext) interface{} {
	cmd := &VmStatusCheckCmd{}
	ctx.GetCommand(cmd)
	vm_status := make(map[string]bool)
	for _, uuid := range cmd.Uuids {
		vm_status[uuid] = isVmStatus(uuid, VM_STATUS_RUNNING)
	}

	return VmStatusCheckRsp{Vm_status: vm_status}
}

func vmSshGuestVmHandler(ctx *server.CommandContext) interface{} {
	cmd := &VmSshGuestVmCmd{}
	ctx.GetCommand(cmd)
	var rsp VmSshGuestVmRsp
	timeout := make(chan VmSshGuestVmRsp, 1)
	go func() {
		output, err := utils.ExecuteCommand(cmd.Ip, "22", cmd.Username, cmd.Password, cmd.Command)
		if err != nil {
			rsp.Success = false
			rsp.Error = fmt.Sprintf("[SSH] unable to ssh in vm[ip:%s], assume its not ready. Exception: %s ", cmd.Ip, err)
			rsp.Result = ""
		} else {
			rsp.Success = true
			rsp.Error = ""
			rsp.Result = output
		}
		timeout <- rsp
	}()

	select {
	case rsp = <-timeout:
	case <-time.After(time.Second * time.Duration(cmd.Timeout)):
		rsp.Success = false
		rsp.Error = fmt.Sprintf("ssh execution keeps failure, until timeout: %d", cmd.Timeout)
		rsp.Result = ""
	}

	return rsp
}

func vmScpGuestVmHandler(ctx *server.CommandContext) interface{} {
	cmd := &VmScpGuestVmCmd{}
	ctx.GetCommand(cmd)
	var rsp VmScpGuestVmRsp
	err := utils.ScpFile(cmd.Ip, "22", cmd.Username, cmd.Password, cmd.SrcFile, cmd.DstFile)
	if err != nil {
		rsp.Success = false
		rsp.Error = fmt.Sprintf("[SSH] unable to ssh to vm[ip:%s]. Exception: %s ", cmd.Ip, err)
	} else {
		rsp.Success = true
		rsp.Error = ""
	}

	return rsp
}

func vmStatusHandler(ctx *server.CommandContext) interface{} {
	cmd := &VmStatusCheckCmd{}
	ctx.GetCommand(cmd)
	vm_status := make(map[string]string)
	for _, uuid := range cmd.Uuids {
		vm_status[uuid] = vmStatus(uuid)
		vm_status[uuid+"_log"] = vmSerialLog(uuid, vmStatus(uuid))
	}

	return VmStatusRsp{Vm_status: vm_status}
}

func listAllVm() []string {
	bash := utils.Bash{
		Command: "virsh list --all",
		NoLog:   true,
	}

	_, o, _, _ := bash.RunWithReturn()
	bash.PanicIfError()
	return strings.Split(o, "\n")
}

func vmListAllVmHandler(ctx *server.CommandContext) interface{} {
	vm_status := make(map[string][]string)
	vm_status["vms"] = listAllVm()
	return VmListAllVmRsp{Vm_status: vm_status}
}

func vmBlkStatus(uuid string) map[string]string {
	bash := utils.Bash{
		Command: fmt.Sprintf("virsh domblklist %s", uuid),
		NoLog:   true,
	}

	_, o, _, _ := bash.RunWithReturn()
	bash.PanicIfError()
	output := strings.Split(o, "\n")
	output = output[2:]
	ret := make(map[string]string)
	for _, item := range output {
		if item != "" {
			blk := strings.Fields(item)
			ret[blk[0]] = blk[1]
		}
	}
	return ret
}

func vmBlkStatusHandler(ctx *server.CommandContext) interface{} {
	cmd := &VmStatusCheckCmd{}
	ctx.GetCommand(cmd)
	vm_status := make(map[string]map[string]string)
	for _, uuid := range cmd.Uuids {
		vm_status[uuid] = vmBlkStatus(uuid)
	}

	return VmBlkStatusRsp{Vm_status: vm_status}
}

func vmEchoHandler(ctx *server.CommandContext) interface{} {
	return nil
}

func vmDeviceQosHandler(ctx *server.CommandContext) interface{} {
	cmd := &VmDiskQosCmd{}
	ctx.GetCommand(cmd)
	bash := utils.Bash{
		Command: fmt.Sprintf("virsh blkdeviotune %s %s", cmd.Uuid, cmd.Dev),
		NoLog:   true,
	}

	_, o, _, _ := bash.RunWithReturn()
	bash.PanicIfError()

	return VmDiskQosRsp{VmDeviceIo: o}
}

func VmEntryPoint() {
	server.RegisterSyncCommandHandler(IS_VM_STOPPED_PATH, vmIsVmStoppedHandler)
	server.RegisterSyncCommandHandler(IS_VM_PAUSED_PATH, vmIsVmSuspendedHandler)
	server.RegisterSyncCommandHandler(IS_VM_DESTROYED_PATH, vmIsVmDestroyedHandler)
	server.RegisterSyncCommandHandler(IS_VM_RUNNING_PATH, vmIsVmRunningHandler)
	server.RegisterSyncCommandHandler(SSH_GUEST_VM_PATH, vmSshGuestVmHandler)
	server.RegisterSyncCommandHandler(SCP_GUEST_VM_PATH, vmScpGuestVmHandler)
	server.RegisterSyncCommandHandler(VM_STATUS, vmStatusHandler)
	server.RegisterSyncCommandHandler(LIST_ALL_VM, vmListAllVmHandler)
	server.RegisterSyncCommandHandler(VM_BLK_STATUS, vmBlkStatusHandler)
	server.RegisterSyncCommandHandler(VM_ECHO_PATH, vmEchoHandler)
	server.RegisterSyncCommandHandler(VM_DEVICE_QOS, vmDeviceQosHandler)
}
