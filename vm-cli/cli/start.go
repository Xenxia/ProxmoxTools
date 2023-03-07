package cli

import (
	"context"
	"strings"
	"vm-cli/vm"

	"github.com/urfave/cli/v2"
)

var cliStart = cli.Command{
	Name:      "start",
	Usage:     "Start virtual machine. <vmid> is the (unique) ID of the VM. Start multiple VM\\CTs with : 100.101",
	UsageText: "vm start <vmid>",

	Before: func(ctx *cli.Context) error {
		if ctx.NArg() < 1 {
			return cli.Exit("One argument attempt", 3)
		}
		if ctx.NArg() >= 2 {
			return cli.Exit("One argument attempt", 3)
		}

		vmid := ctx.Args().First()

		if strings.Contains(vmid, ".") {
			ctx.Context = context.WithValue(ctx.Context, "vmid", strings.Split(vmid, "."))
		} else {
			ctx.Context = context.WithValue(ctx.Context, "vmid", []string{vmid})
		}

		return nil
	},

	Action: func(ctx *cli.Context) error {

		ms := vm.Get_Machines()

		for _, id := range ctx.Context.Value("vmid").([]string) {

			m, _ := ms.Get_Machine(id)
			m.Start()
		}

		return nil
	},
}