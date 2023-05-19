package vm

import (
	"strconv"
	"vm-cli/util"
)

func (m Machine) Start() bool {

	if m.Type == "QM" {
		_, _ = util.Pvesh_post("/nodes/"+HOST+"/qemu/"+m.Vmid+"/status/start",
			[]string{"-timeout", "10"},
			"string",
		)
		return true
	}

	if m.Type == "LXC" {
		_, _ = util.Pvesh_post("/nodes/"+HOST+"/lxc/"+m.Vmid+"/status/start",
			[]string{},
			"string",
		)
		return true
	}
	return false
}

func (m Machine) Stop(force bool) bool {

	if m.Type == "QM" {
		_, _ = util.Pvesh_post("/nodes/"+HOST+"/qemu/"+m.Vmid+"/status/shutdown", 
			[]string{"-timeout", "30", "-forcestop", strconv.Itoa(int(util.B2i(force)))}, 
			"string",
		)
		return true
	}

	if m.Type == "LXC" {
		_, _ = util.Pvesh_post("/nodes/"+HOST+"/lxc/"+m.Vmid+"/status/shutdown", 
			[]string{"-timeout", "10", "-forcestop", strconv.Itoa(int(util.B2i(force)))},
			"string",
		)
		return true
	}
	return false
}

func (m Machine) Reboot() bool {

	if m.Type == "QM" {
		_, _ = util.Pvesh_post("/nodes/"+HOST+"/qemu/"+m.Vmid+"/status/reboot", 
			[]string{"-timeout", "30"}, 
			"string",
		)
		return true
	}

	if m.Type == "LXC" {
		_, _ = util.Pvesh_post("/nodes/"+HOST+"/lxc/"+m.Vmid+"/status/reboot", 
			[]string{"-timeout", "10"},
			"string",
		)
		return true
	}
	return false
}


