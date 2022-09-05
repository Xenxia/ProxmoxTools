package cli

import (
	"os"
	"strings"
	"vm-cli/vm"

	"github.com/olekukonko/tablewriter"
	"github.com/urfave/cli/v2"
	"golang.org/x/exp/slices"
)

var cliList = cli.Command{
	Name:      "list",
	Usage:     "show list of VM and Container",
	UsageText: "vm list [Command options]",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:        "sort",
			Aliases:     []string{"s"},
			Usage:       "['status', 'type', 'name', 'id']",
			DefaultText: "id",
		},
		&cli.BoolFlag{
			Name:    "reverse",
			Aliases: []string{"r"},
			Usage:   "reverse sort",
		},
	},
	Before: func(ctx *cli.Context) error {

		if slices.Contains(ctx.FlagNames(), "sort") {
			vv := []string{"status", "type", "name", "id"}
			ok := false

			for _, value := range vv {
				if value == ctx.String("sort") {
					ok = true
				}
			}
			if !ok {
				return cli.Exit("use valide value ["+strings.Join(vv, ", ")+"]", 3)
			}
		}

		return nil
	},
	Action: func(ctx *cli.Context) error {

		var data [][]string

		v := vm.Get()

		data = vm.Format(v)

		println("\n")

		table := tablewriter.NewWriter(os.Stdout)
		table.SetHeader([]string{"VMID", "Status", "Type", "Name", "Uptime"})
		table.SetBorders(tablewriter.Border{Left: false, Top: false, Right: false, Bottom: false})
		table.SetCenterSeparator("┿")
		table.SetColumnSeparator("│")
		table.SetRowSeparator("━")
		table.SetAlignment(tablewriter.ALIGN_LEFT)

		for _, d := range data {
			if d[1] == "stopped" {
				table.Rich(d, []tablewriter.Colors{{}, {tablewriter.Normal, tablewriter.FgRedColor}, {}, {}, {}})
			} else if d[1] == "running" {
				table.Rich(d, []tablewriter.Colors{{}, {tablewriter.Normal, tablewriter.FgGreenColor}, {}, {}, {}})
			} else {
				table.Append(d)
			}
			
		}
		table.Render()

		println("\n")

		return nil
	},
}
