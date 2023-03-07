package vm

import (
	"fmt"
	"vm-cli/util"
)

func (m Machine) Start() bool {

	t, _ := util.Pvesh_post("/nodes/"+HOST+"/qemu/"+m.vmid+"/status/start", "string")

	fmt.Println(t)
	return true
}