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
	Vmid string;
	Status string;
	Type string;
	Name string;
	Uptime float64;
}

type Machines struct {
	Machines []Machine
}

var wg sync.WaitGroup

func Get_Machines() Machines {
	var ms []Machine

	wg.Add(2)
	go Get_VM_info(&ms)
	go Get_CT_info(&ms)

	wg.Wait()

	sort.Slice(ms, func(i, j int) bool {
		return ms[i].Vmid < ms[j].Vmid
	})

	return Machines{
		Machines: ms,
	}
}

func Get_VM_info(in *[]Machine) {
	defer wg.Done()

	result, _ := util.Pvesh_get("/nodes/"+HOST+"/qemu")

	for _, v := range result.([]interface{}) {

		v := v.(map[string]interface{})

		vm := Machine{
			Vmid: fmt.Sprintf("%v", v["vmid"]),
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
			Vmid: fmt.Sprintf("%v", v["vmid"]),
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

	for _, v := range m.Machines {
		list := []string{}

		list = append(list, v.Vmid)
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

	for _, v := range m.Machines {
		if vmid == v.Vmid {
			return v, true
		}
	}

	log.Fatal("| VM ID " + vmid + " Not existe")
	return Machine{}, false
}

func (m *Machine) Update() {

	var result any

	if m.Type == "QM" {
		result, _ = util.Pvesh_get("/nodes/"+HOST+"/qemu/"+m.Vmid+"/status/current")
	} else {
		result, _ = util.Pvesh_get("/nodes/"+HOST+"/lxc/"+m.Vmid+"/status/current")
	}

	m.Status = result.(map[string]any)["status"].(string)
}

