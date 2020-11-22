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

version="2.0.0"

#? Color ------------------------------------------------------------------------------->
class Co:
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

parser_start = subparsers.add_parser('start', help="<vmID> Start VM")
parser_start.add_argument('vmID', type=int, help='The (unique) ID of the VM.')

parser_stop = subparsers.add_parser('stop', help='<vmID> Stop VM')
parser_stop.add_argument('vmID', type=int, help='The (unique) ID of the VM.')

parser_reboot = subparsers.add_parser('reboot', help='<vmID> Reboot VM')
parser_reboot.add_argument('vmID', type=int, help='The (unique) ID of the VM.')

parser_console = subparsers.add_parser('console', help="<vmID> Open console vm 'for lxc vm'")
parser_console.add_argument('vmID', type=int, help='The (unique) ID of the VM.')

parser_destroy = subparsers.add_parser('destroy', help="<vmID> [OPTION] Destroy the container (also delete all uses files).")
parser_destroy.add_argument('vmID', type=int, help='The (unique) ID of the VM.')
parser_destroy.add_argument('-p', '-purge', action="store_true", dest='Purge', help='Remove container from all related configurations.')

parser_clone = subparsers.add_parser('clone', help="<vmID> <newID> [OPTION] Create a container clone/copy")
parser_clone.add_argument('vmID', type=int, help='The (unique) ID of the VM.')
parser_clone.add_argument('newID', type=int, help='vmID for the clone.')
parser_clone.add_argument('-bwlimit', type=int, help='Override I/O bandwidth limit (in KiB/s).')
parser_clone.add_argument('-description', type=str, help='Description for the new CT/VM.')
parser_clone.add_argument('-full', action="store_true", help='Create a full copy of all disks. This is always done when you clone a normal CT/VM. For CT templates, we try to create a linked clone by default.')
parser_clone.add_argument('-name', type=str, help='Set a hostname/name for the new CT/VM.')
parser_clone.add_argument('-pool', type=str, help='Add the new CT to the specified pool.')
parser_clone.add_argument('-snapname', type=str, help='The name of the snapshot.')
parser_clone.add_argument('-storage', type=str, help='Target storage for full clone.')
parser_clone.add_argument('-target', type=str, help='Target node. Only allowed if the original VM is on shared storage.')
parser_clone.add_argument('-format', choices=['qcow2', 'raw', 'vmdk'], help='Target format for file storage. Only valid for full clone. (Only QEMU VM)')

group = parser.add_mutually_exclusive_group()
group.add_argument('-v', '--version', action='version', version=Co.Green+version+Co.Default)
group.add_argument("-l", "--list", action="store_true", help ="shows the list of all VMs")

args = parser.parse_args()
#? Class ----------------------------------------------------------------------------------------->

class Sys:
  
    def clear():
      _ = system('clear')

    def exit():
        raise SystemExit(0)

class Vm:
  
    __vm_dico = {}

    def __init__(self):

        self.__vm_dico[0] = {'#1' : 'VMID', '#2' : 'Status', '#3' : 'Type', '#4' : 'Name'}
        List_pct = os.popen("pct list", "r").read();
        List_qm = os.popen("qm list", "r").read();
        num_dict = int(1);

        ###############
        # VM LXC LIST #
        ###############

        for ligne in List_pct.split("\n"):
            num = int(1)
            self.__vm_dico[num_dict] = {'vm_ID' : '', 'Status' : '', 'Tag' : '', 'Name' : ''}
            
            for string in ligne.split(" "):
            
                if string != "" and string != "VMID" and string != "Status" and string != "Lock" and string != "Name":

                    if num == 1:
                        self.__vm_dico[num_dict]['vm_ID'] = string

                    if num == 2:
                        self.__vm_dico[num_dict]['Status'] = string

                    if num == 3:
                        self.__vm_dico[num_dict]['Name'] = string
                        self.__vm_dico[num_dict]['Tag'] = "LXC"
                        num_dict+= 1

                    num+= 1

        ################
        # VM QEMU LIST #
        ################

        for ligne in List_qm.split("\n"):
            num = int(1)
            self.__vm_dico[num_dict] = {'vm_ID' : '', 'Status' : '', 'Tag' : '', 'Name' : ''}
            
            for string in ligne.split(" "):
            
                if string != "" and string != "VMID" and string != "STATUS" and string != "NAME" and string != "MEM(MB)" and string != "BOOTDISK(GB)" and string != "PID":

                    if num == 1:
                        self.__vm_dico[num_dict]['vm_ID'] = string

                    if num == 2:
                        self.__vm_dico[num_dict]['Name'] = string

                    if num == 3:
                        self.__vm_dico[num_dict]['Status'] = string
                        self.__vm_dico[num_dict]['Tag'] = "QM"
                        num_dict+= 1

                    num+= 1

    def __check_ID(self, ID_vm):
  
        if int(ID_vm) >= 100 and int(ID_vm) <= 999:
            return ID_vm
        
        print(Co.Red+str(ID_vm)+' ID incorect'+Co.Reset)
        Sys.exit()
  
    def used_ID(self, ID_vm):

        self.__check_ID(ID_vm)
        num_vm_len = len(self.__vm_dico)

        for x in range(1,num_vm_len):
            for valeur in self.__vm_dico[x].values():
                if valeur == str(ID_vm):
                    print(Co.Orange+'The ID "'+str(ID_vm)+'" is already used by another VM'+Co.Reset)
                    Sys.exit()

    def search(self, ID_vm):

        self.__check_ID(ID_vm)
        num_vm_len = len(self.__vm_dico)

        for x in range(1,num_vm_len):
            for valeur in self.__vm_dico[x].values():
                if valeur == str(ID_vm):
                    return self.__vm_dico[x]
                
        print(Co.Red+"No existing VM"+Co.Reset)
        Sys.exit()

    def getDico(self):

        return self.__vm_dico

#? Fonction ----------------------------------------------------------------------------------------->
def start_VM(vm):

    if vm["Status"] == "running":
        print(Co.Magenta+"VM Already "+Co.Green+"started "+Co.Magenta+vm["Name"]+':'+vm["vm_ID"]+Co.Reset)

    elif vm["Tag"] == "LXC":
        print(Co.Yellow+"Start Container "+vm["Name"]+':'+vm["vm_ID"]+Co.Default)
        os.system('pct start '+ str(vm["vm_ID"]))
        print(Co.Green+"Started Container "+vm["Name"]+':'+vm["vm_ID"]+Co.Reset)

    elif vm["Tag"] == "QM":
        print(Co.Yellow+"Start VM "+vm["Name"]+':'+vm["vm_ID"]+Co.Default)
        os.system('qm start '+ str(vm["vm_ID"]))
        print(Co.Green+"Started VM "+vm["Name"]+':'+vm["vm_ID"]+Co.Reset)

def stop_VM(vm):

    if vm["Status"] == "stopped":
        print(Co.Magenta+"VM Already "+Co.Red+"stopped "+Co.Magenta+vm["Name"]+':'+vm["vm_ID"]+Co.Reset)

    elif vm["Tag"] == "LXC":
        print(Co.Yellow+"Stop Container "+vm["Name"]+':'+vm["vm_ID"]+Co.Default)
        os.system('pct stop '+ str(vm["vm_ID"]))
        print(Co.Green+"Stopped Container "+vm["Name"]+':'+vm["vm_ID"]+Co.Reset)

    elif vm["Tag"] == "QM":
        print(Co.Yellow+"Stop VM "+vm["Name"]+':'+vm["vm_ID"]+Co.Default)
        os.system('qm stop '+ str(vm["vm_ID"]))
        print(Co.Green+"Stopped VM "+vm["Name"]+':'+vm["vm_ID"]+Co.Reset)

def reboot_VM(vm):

    if vm["Status"] == "stopped":
        print(Co.Magenta+"The VM is "+Co.Red+"stopped "+Co.Magenta+vm["Name"]+':'+vm["vm_ID"]+Co.Reset)

    elif vm["Tag"] == "LXC":
        print(Co.Yellow+"Reboot Container "+vm["Name"]+':'+vm["vm_ID"]+Co.Default)
        os.system('pct reboot '+ str(vm["vm_ID"]))
        print(Co.Green+"Rebooted Container "+vm["Name"]+':'+vm["vm_ID"]+Co.Reset)

    elif vm["Tag"] == "QM":
        print(Co.Yellow+"Reboot VM "+vm["Name"]+':'+vm["vm_ID"]+Co.Default)
        os.system('qm reboot '+ str(vm["vm_ID"]))
        print(Co.Green+"Rebooted VM "+vm["Name"]+':'+vm["vm_ID"]+Co.Reset)


def console_VM(vm):

    if vm["Status"] == "stopped":
        print(Co.Magenta+"The VM is "+Co.Red+"stopped "+Co.Magenta+vm["Name"]+':'+vm["vm_ID"]+Co.Reset)

    elif vm["Tag"] == "LXC":
        print(Co.Yellow+"exit the console Ctrl+a q"+Co.Reset)
        os.system('pct console '+ str(vm["vm_ID"])+' -escape ^a')
        Sys.clear()

    elif vm["Tag"] == "QM":
        print(Co.Yellow+"use 'qm terminal' and config serial"+Co.Reset)

def destroy_VM(vm, opti=""):

    if vm["Status"] == "running":
        print(Co.Magenta+"The VM is "+Co.Green+"running "+Co.Magenta+vm["Name"]+':'+vm["vm_ID"]+Co.Reset)
        Sys.exit()

    choiced_Action = input(Co.Orange+"Do you really want to remove the VM : "+Co.UnderLine+Co.Cyan+vm["Name"]+Co.Default+" ("+Co.Green+"Y"+Co.Default+"/"+Co.Red+"[N]"+Co.Default+"): ")
    print()

    if choiced_Action == 'Y' or choiced_Action == 'y' :

        input_vmID = input(Co.Magenta+"Please enter the ID to confirm"+Co.Default+" ("+vm["vm_ID"]+") : ")

        if input_vmID == vm["vm_ID"]:
            print(Co.Reset)
            if vm["Tag"] == "LXC":
                os.system('pct destroy '+ str(vm["vm_ID"])+opti)

            elif vm["Tag"] == "QM":
                os.system('qm destroy '+ str(vm["vm_ID"])+opti)
        else:
            print(Co.Red+'Wrong ID : '+input_vmID+Co.Reset)
            Sys.exit()
        
        print()

    else:
        print()
        Sys.exit()

def clone_VM(vm, new_vm, opti=""):

    if vm["Status"] == "running":
        print(Co.Magenta+"The VM is "+Co.Green+"running "+Co.Magenta+vm["Name"]+':'+vm["vm_ID"]+Co.Reset)
        Sys.exit()

    if vm["Tag"] == "LXC":
        print()
        os.system('pct clone '+str(vm["vm_ID"])+' '+str(new_vm)+opti)

    elif vm["Tag"] == "QM":
        print()
        os.system('qm clone '+ str(vm["vm_ID"])+' '+str(new_vm)+opti)

    print()
    Sys.exit()

#? Start ----------------------------------------------------------------------------------------->

print()

vm = Vm()
option = ""

if args.Command_Name == 'start':

    vm_info = vm.search(args.vmID)
    start_VM(vm_info)
    Sys.exit()

if args.Command_Name == 'stop':

    vm_info = vm.search(args.vmID)
    stop_VM(vm_info)
    Sys.exit()

if args.Command_Name == 'reboot':

    vm_info = vm.search(args.vmID)
    reboot_VM(vm_info)
    Sys.exit()

if args.Command_Name == 'console':

    vm_info = vm.search(args.vmID)
    console_VM(vm_info)
    Sys.exit()

if args.Command_Name == 'destroy':

    vm_info = vm.search(args.vmID)
    if args.Purge: option = " -purge "
    destroy_VM(vm_info, option)
    Sys.exit()

if args.Command_Name == 'clone':

    vm.used_ID(args.newID)
    vm_info = vm.search(args.vmID)

    if args.bwlimit: option+= " -bwlimit "+str(args.bwlimit)
    if args.description: option+= " -description "+str(args.description)
    if args.full: option+= " -full"
    if args.pool: option+= " -pool "+str(args.pool)
    if args.snapname: option+= " -snapname "+str(args.snapname)
    if args.storage: option+= " -storage "+str(args.storage)
    if args.target: option+= " -target "+str(args.target)
    if args.name: #-------------------------->
        if vm_info["Tag"] == "LXC":
            option+= " -hostname "+args.name
        elif vm_info["Tag"] == "QM":
            option+= " -name "+args.name
    if args.format: #-------------------------->
        if vm_info["Tag"] == "QM":
            option+= " -format "+args.format
        else:
            print(Co.Orange+'The "-format" option is only available for VM (QEMU)'+Co.Reset)
            Sys.exit()

    clone_VM(vm_info, args.newID, option)
    Sys.exit()

if args.list:

    Sys.clear()
    print("\n")

    vm_dico = vm.getDico()

    num_vm_len = len(vm_dico)

    form_header = "{0:6}{1:10}{2:6}{3:10}"
    form_Stop = "{0:6}"+Co.Red+"{1:10}"+Co.Default+"{2:6}{3:10}"
    form_Start = "{0:6}"+Co.Green+"{1:10}"+Co.Default+"{2:6}{3:10}"
    dash = '-' * 40

    for x in range(0,num_vm_len-1):

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
    
    print(Co.Reset)

    Sys.exit()

print(Co.Red+'No argument detected'+Co.Reset)

parser.print_help()

print('\n')