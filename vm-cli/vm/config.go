package vm

import (
	"vm-cli/util"
)

type Config struct {
	name    string
	cores   int
	ram     int
	network string
	osType  string
	digest  string
}

func Get_VM_config(vmid string) Config {
	c, _ := util.Pvesh_get("/nodes/" + HOST + "/qemu/" + vmid + "/config")

	config := c.(map[string]interface{})

	return Config{
		name: config["name"].(string),
		cores: int(config["cores"].(float64)),
		ram: int(config["memory"].(float64)),
		network: config["net0"].(string),
		osType: config["ostype"].(string),
		digest: config["digest"].(string),
	}
}

func Get_CT_config(vmid string) Config {
	c, _ := util.Pvesh_get("/nodes/" + HOST + "/lxc/" + vmid + "/config")

	config := c.(map[string]interface{})


	return Config{
		name: config["hostname"].(string),
		cores: int(config["cores"].(float64)),
		ram: int(config["memory"].(float64)),
		network: config["net0"].(string),
		osType: config["ostype"].(string),
		digest: config["digest"].(string),
	}

}

func Get_config(vmid string) Config {
	machine, _ := Get_Machines().Get_Machine(vmid)

	if machine.Type == "QM" {
		return Get_VM_config(vmid)
	}
	return Get_CT_config(vmid)
}
