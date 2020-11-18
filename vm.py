#!/usr/bin/env python3

# MIT License

# Copyright (c) 2020 Xenxia

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os, sys, argparse
from os import system, name
from time import sleep

version="1.2.0"

#? Color ------------------------------------------------------------------------------->
class co:
    Reset = "\u001b[0m"+"\n"

    Default         = "\u001b[0m"
    Black           = "\u001b[38;5;0m"
    white           = "\u001b[38;5;255m"
    Red             = "\u001b[38;5;160m"
    Green           = "\u001b[38;5;82m"
    Yellow          = "\u001b[38;5;226m"
    Orange          = "\u001b[38;5;208m"
    Blue            = "\u001b[38;5;27m"
    Magenta         = "\u001b[38;5;207m"
    Cyan            = "\u001b[38;5;51m"

    Bold            = '\033[1m'
    UnderLine       = '\033[4m'
    Reverse         = "\033[;7m"

#? Argument parser ------------------------------------------------------------------------------->
parser = argparse.ArgumentParser(description="Application to merge the 'qm' and 'pct' commands from proxmox",
                                allow_abbrev=False,
                                prog='vm',
                                usage="%(prog)s"
                                )

subparsers = parser.add_subparsers(title ='Commande',
                                  dest='Command_Name',
                                  )

parser_start = subparsers.add_parser('start', help="<VMID> Start VM")
parser_start.add_argument('VMID', type=int, help='ID VM')

parser_stop = subparsers.add_parser('stop', help='<VMID> Stop VM')
parser_stop.add_argument('VMID', type=int, help='ID VM')

parser_reboot = subparsers.add_parser('reboot', help='<VMID> Reboot VM')
parser_reboot.add_argument('VMID', type=int, help='ID VM')

parser_console = subparsers.add_parser('console', help="<VMID> Open console vm 'for lxc vm'")
parser_console.add_argument('VMID', type=int, help='ID VM')

parser_destroy = subparsers.add_parser('destroy', help="<VMID> [-purge] Destroy the container (also delete all uses files).")
parser_destroy.add_argument('VMID', type=int, help='ID VM')
parser_destroy.add_argument('-p', '-purge', action="store_true", dest='Purge', help='Remove container from all related configurations.')

group = parser.add_mutually_exclusive_group()
group.add_argument('-v', '--version', action='version', version=co.Green+version+co.Default)
group.add_argument("-l", "--list", action="store_true", help ="shows the list of all VMs")

args = parser.parse_args()

#? Fonction ----------------------------------------------------------------------------------------->
def Clear():
    _ = system('clear')

def Exit():
    raise SystemExit(0)

def List_vm():

    vm_dico = {}
    vm_dico[0] = {'#1' : 'VMID', '#2' : 'Status', '#3' : 'Type', '#4' : 'Name'}
    List_pct = os.popen("pct list", "r").read();
    List_qm = os.popen("qm list", "r").read();
    num_dict = int(1);

    ###############
    # VM LXC LIST #
    ###############

    for ligne in List_pct.split("\n"):
        num = int(1)
        vm_dico[num_dict] = {'VM_ID' : '', 'Status' : '', 'Tag' : '', 'Name' : ''}
        
        for string in ligne.split(" "):
        
            if string != "" and string != "VMID" and string != "Status" and string != "Lock" and string != "Name":

                if num == 1:
                    vm_dico[num_dict]['VM_ID'] = string

                if num == 2:
                    vm_dico[num_dict]['Status'] = string

                if num == 3:
                    vm_dico[num_dict]['Name'] = string
                    vm_dico[num_dict]['Tag'] = "LXC"
                    num_dict = num_dict+1

                num = num+1

    ################
    # VM QEMU LIST #
    ################

    for ligne in List_qm.split("\n"):
        num = int(1)
        vm_dico[num_dict] = {'VM_ID' : '', 'Status' : '', 'Tag' : '', 'Name' : ''}
        
        for string in ligne.split(" "):
        
            if string != "" and string != "VMID" and string != "STATUS" and string != "NAME" and string != "MEM(MB)" and string != "BOOTDISK(GB)" and string != "PID":

                if num == 1:
                    vm_dico[num_dict]['VM_ID'] = string

                if num == 2:
                    vm_dico[num_dict]['Name'] = string

                if num == 3:
                    vm_dico[num_dict]['Status'] = string
                    vm_dico[num_dict]['Tag'] = "QM"
                    num_dict = num_dict+1

                num = num+1

    return vm_dico

def Check_IDVM(ID_vm):

    if int(ID_vm) >= 100 and int(ID_vm) <= 999:
        return ID_vm
    
    print(co.Red+str(ID_vm)+' ID incorect'+co.Reset)
    Exit()

def Search_VM(ID_vm):

    vm_dico = List_vm()
    num_vm_pct = len(vm_dico)

    for x in range(1,num_vm_pct):
        for valeur in vm_dico[x].values():
            if valeur == str(ID_vm):
                return vm_dico[x]
            
    print(co.Red+"No vm"+co.Reset)
    Exit()

def Start_VM(vm):

    if vm["Status"] == "running":
        print(co.Magenta+"VM Already "+co.Green+"started "+co.Magenta+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

    elif vm["Tag"] == "LXC":
        print(co.Yellow+"Start Container "+vm["Name"]+':'+vm["VM_ID"]+co.Default)
        os.system('pct start '+ str(vm["VM_ID"]))
        print(co.Green+"Started Container "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

    elif vm["Tag"] == "QM":
        print(co.Yellow+"Start VM "+vm["Name"]+':'+vm["VM_ID"]+co.Default)
        os.system('qm start '+ str(vm["VM_ID"]))
        print(co.Green+"Started VM "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

def Stop_VM(vm):

    if vm["Status"] == "stopped":
        print(co.Magenta+"VM Already "+co.Red+"stopped "+co.Magenta+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

    elif vm["Tag"] == "LXC":
        print(co.Yellow+"Stop Container "+vm["Name"]+':'+vm["VM_ID"]+co.Default)
        os.system('pct stop '+ str(vm["VM_ID"]))
        print(co.Green+"Stopped Container "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

    elif vm["Tag"] == "QM":
        print(co.Yellow+"Stop VM "+vm["Name"]+':'+vm["VM_ID"]+co.Default)
        os.system('qm stop '+ str(vm["VM_ID"]))
        print(co.Green+"Stopped VM "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

def Reboot_VM(vm):

    if vm["Status"] == "stopped":
        print(co.Magenta+"The VM is "+co.Red+"stopped "+co.Magenta+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

    elif vm["Tag"] == "LXC":
        print(co.Yellow+"Reboot Container "+vm["Name"]+':'+vm["VM_ID"]+co.Default)
        os.system('pct reboot '+ str(vm["VM_ID"]))
        print(co.Green+"Rebooted Container "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

    elif vm["Tag"] == "QM":
        print(co.Yellow+"Reboot VM "+vm["Name"]+':'+vm["VM_ID"]+co.Default)
        os.system('qm reboot '+ str(vm["VM_ID"]))
        print(co.Green+"Rebooted VM "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)


def Console_VM(vm):

    if vm["Status"] == "stopped":
        print(co.Magenta+"The VM is "+co.Red+"stopped "+co.Magenta+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

    elif vm["Tag"] == "LXC":
        print(co.Yellow+"Exit the console Ctrl+a q"+co.Reset)
        os.system('pct console '+ str(vm["VM_ID"])+' -escape ^a')
        Clear()

    elif vm["Tag"] == "QM":
        print(co.Yellow+"use 'qm terminal' and config serial"+co.Reset)

def Destroy_VM(vm, opti=""):

    if vm["Status"] == "running":
        print(co.Magenta+"The VM is "+co.Green+"running "+co.Magenta+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

    choiced_Action = input(co.Orange+"Do you really want to remove the VM : "+co.UnderLine+co.Cyan+vm["Name"]+co.Default+" ("+co.Green+"Y"+co.Default+"/"+co.Red+"[N]"+co.Default+"): ")
    print()

    if choiced_Action == 'Y' or choiced_Action == 'y' :

        input_VMID = input(co.Magenta+"Please enter the ID to confirm"+co.Default+" ("+vm["VM_ID"]+") : ")

        if input_VMID == vm["VM_ID"]:
            print(co.Reset)
            if vm["Tag"] == "LXC":
                os.system('pct destroy '+ str(vm["VM_ID"])+' '+opti)

            elif vm["Tag"] == "QM":
                os.system('qm destroy '+ str(vm["VM_ID"])+' '+opti)

        print()
        Exit()

    else:
        Exit()


#? Start ----------------------------------------------------------------------------------------->

print()

option = ""

if args.Command_Name == 'start':

    vm_info = Search_VM(Check_IDVM(args.VMID))
    Start_VM(vm_info)
    Exit()

if args.Command_Name == 'stop':

    vm_info = Search_VM(Check_IDVM(args.VMID))
    Stop_VM(vm_info)
    Exit()

if args.Command_Name == 'reboot':

    vm_info = Search_VM(Check_IDVM(args.VMID))
    Reboot_VM(vm_info)
    Exit()

if args.Command_Name == 'console':

    vm_info = Search_VM(Check_IDVM(args.VMID))
    Console_VM(vm_info)
    Exit()

if args.Command_Name == 'destroy':

    vm_info = Search_VM(Check_IDVM(args.VMID))
    if args.Purge: option = "-purge "
    Destroy_VM(vm_info, option)
    Exit()

if args.list:

    Clear()
    print("\n")

    vm_dico = List_vm()

    num_vm_pct = len(vm_dico)

    form_header = "{0:6}{1:10}{2:6}{3:10}"
    form_Stop = "{0:6}"+co.Red+"{1:10}"+co.Default+"{2:6}{3:10}"
    form_Start = "{0:6}"+co.Green+"{1:10}"+co.Default+"{2:6}{3:10}"
    dash = '-' * 40

    for x in range(0,num_vm_pct-1):

        vm_print = list(vm_dico[x].values())

        if x != 0:
            if vm_print[1] == 'stopped':
                print(form_Stop.format(*vm_print))
            elif vm_print[1] == 'running':
                print(form_Start.format(*vm_print))
        else:
            print(dash)
            print(form_header.format(*vm_print))
            print(dash)
    
    print(co.Reset)

    Exit()

print(co.Red+'No argument detected'+co.Reset)

parser.print_help()

print('\n')