package vm

import (
	"fmt"
	"log"
	"sort"
	"sync"
	"time"
	"vm-cli/util"
)

type Machine struct{
	vmid string;
	Status string;
	Type string;
	Name string;
	Uptime float64;
}

type Machines struct {
	machines []Machine
}

var wg sync.WaitGroup

func Get_Machines() Machines {
	var ms []Machine

	wg.Add(2)
	go Get_VM_info(&ms)
	go Get_CT_info(&ms)

	wg.Wait()

	return Machines{
		machines: ms,
	}
}

func Get_VM_info(in *[]Machine) {
	defer wg.Done()

	result, _ := util.Pvesh_get("/nodes/"+HOST+"/qemu")

	for _, v := range result.([]interface{}) {

		v := v.(map[string]interface{})

		vm := Machine{
			vmid: fmt.Sprintf("%v", v["vmid"]),
			Status: v["status"].(string),
			Type: "QM",
			Name: v["name"].(string),
			Uptime: v["uptime"].(float64),
		}
		*in = append(*in, vm)
	}
}

func Get_CT_info(in *[]Machine) {
	defer wg.Done()

	result, _ := util.Pvesh_get("/nodes/"+HOST+"/lxc")

	for _, v := range result.([]interface{}) {

		v := v.(map[string]interface{})

		vm := Machine{
			vmid: fmt.Sprintf("%v", v["vmid"]),
			Status: v["status"].(string),
			Type: "LXC",
			Name: v["name"].(string),
			Uptime: v["uptime"].(float64),
		}
		*in = append(*in, vm)
	}
}

func (m Machines) Format_machinesToString() [][]string {
	var out [][]string

	for _, v := range m.machines {
		list := []string{}

		list = append(list, v.vmid)
		list = append(list, v.Status)
		list = append(list, v.Type)
		list = append(list, v.Name)
		t := time.Duration(int64(v.Uptime * float64(time.Second)))
		list = append(list, t.String())

		out = append(out, list)

	}

	sort.Slice(out, func(i, j int) bool {
		return out[i][0] < out[j][0] 
	})

	return out
}

func (m Machines) Get_Machine(vmid string) (Machine, bool) {

	for _, v := range m.machines {
		if vmid == v.vmid {
			return v, true
		}
	}

	log.Fatal("| VM ID " + vmid + " Not existe")
	return Machine{}, false
}

