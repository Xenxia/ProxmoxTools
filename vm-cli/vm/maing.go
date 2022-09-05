package vm

import (
	"vm-cli/util"
	"fmt"
	"os"
	"sort"
	"sync"
)


type VM struct{
    ID float64;
    Status string;
    Type string;
    Name string;
    Uptime float64;
}

type CT struct{
    ID float64;
    Status string;
    Type string;
    Name string;
    Uptime float64;
}

type VM_CT struct{
    VM []VM;
    CT []CT;
}

var VMCT VM_CT;
var HOST, _ = os.Hostname()
var wg sync.WaitGroup


func Get() VM_CT {
    var vm_m []VM
    var ct_m []CT

    wg.Add(2)
    go Get_Info_VM(&vm_m)
    go Get_Info_Container(&ct_m)

    wg.Wait()

    return VM_CT{
        VM: vm_m,
        CT: ct_m,
    }
}

func Get_Info_VM(in *[]VM) {
    defer wg.Done()

    result := util.Pvesh_get("/nodes/"+HOST+"/qemu")

    for _, v := range result {

        vm := VM{
            ID: v["vmid"].(float64),
            Status: v["status"].(string),
            Type: "QM",
            Name: v["name"].(string),
            Uptime: v["uptime"].(float64),
        }
        *in = append(*in, vm)
    }

}

func Get_Info_Container(in *[]CT) {
    defer wg.Done()

    result := util.Pvesh_get("/nodes/"+HOST+"/lxc")

    for _, v := range result {

        vm := CT{
            ID: v["vmid"].(float64),
            Status: v["status"].(string),
            Type: "LXC",
            Name: v["name"].(string),
            Uptime: v["uptime"].(float64),
        }
        *in = append(*in, vm)
    }
}

func Format(in VM_CT) [][]string {
    var out [][]string

    for _, v := range in.VM {
        list := []string{}


        list = append(list, fmt.Sprintf("%s", v.ID))
        list = append(list, v.Status)
        list = append(list, v.Type)
        list = append(list, v.Name)
        list = append(list, fmt.Sprintf("%s", v.Uptime))

        out = append(out, list)

    }

    for _, v := range in.CT {
        list := []string{}


        list = append(list, fmt.Sprintf("%s", v.ID))
        list = append(list, v.Status)
        list = append(list, v.Type)
        list = append(list, v.Name)
        list = append(list, fmt.Sprintf("%s", v.Uptime))

        out = append(out, list)

    }


    sort.Slice(out, func(i, j int) bool {
        return out[i][0] < out[j][0]
    })

    return out
}

