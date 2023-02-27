package cli

import (
	"os"
	"sort"
	"strings"
	"vm-cli/vm"

	"github.com/olekukonko/tablewriter"
	"github.com/urfave/cli/v2"
	"golang.org/x/exp/slices"
)

var sortBy int8 = 0

var cliList = cli.Command{
	Name:      "list",
	Usage:     "show list of VM and Container",
	UsageText: "vm list [Command options]",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:        "sort",
			Aliases:     []string{"s"},
			Usage:       "['id', 'status', 'type', 'name', 'uptime']",
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
			vv := []string{"id", "status", "type", "name", "uptime"}
			ok := false

			for _, value := range vv {
				if value == ctx.String("sort") {
					ok = true
					switch value {
						case "id": sortBy = 0
						case "status": sortBy = 1
						case "type": sortBy = 2
						case "name": sortBy = 3
						case "uptime": sortBy = 4
					}
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

		if ctx.Bool("reverse") {
			sort.Slice(data, func(i, j int) bool {
				return data[i][sortBy] > data[j][sortBy] 
			})
		} else {
			sort.Slice(data, func(i, j int) bool {
				return data[i][sortBy] < data[j][sortBy] 
			})
		}

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
