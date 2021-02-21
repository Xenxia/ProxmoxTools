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

import argparse
import os
from os import system
from operator import itemgetter

version = "3.0.0"


# ? Color ------------------------------------------------------------------------------->
class Color:
    RESET = "\u001b[0m" + "\n"

    DEFAULT = "\u001b[0m"
    BLACK = "\u001b[38;5;0m"
    WHITE = "\u001b[38;5;255m"
    RED = "\u001b[38;5;160m"
    GREEN = "\u001b[38;5;82m"
    YELLOW = "\u001b[38;5;226m"
    ORANGE = "\u001b[38;5;208m"
    BLUE = "\u001b[38;5;27m"
    MAGENTA = "\u001b[38;5;207m"
    CYAN = "\u001b[38;5;51m"

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    REVERSE = "\033[;7m"

# ? Argument parser ------------------------------------------------------------------------------->

parser = argparse.ArgumentParser(description="Application to merge the 'qm', 'pct' and 'vz' commands from proxmox",
                                 allow_abbrev=False,
                                 prog='vm',
                                 usage="%(prog)s"
                                 )

subparsers = parser.add_subparsers(title='Commande',
                                   dest='Command_Name',
                                   )

parser_list = subparsers.add_parser('list', help="[OPTION] shows the list of all VMs")
parser_list.add_argument('-sort', choices=['status', 'type', 'name'],
                            help='Default sort by ID VM'
                            'status = sort by STATUS VM running/stopped'
                            'type = sort by TYPE VM : LXC/QM'
                            'name = sort by NAME VM'
                            )
parser_list.add_argument('-r', '-reverse', action="store_true", dest='REVERSE',
                            help='reverse sort.')

parser_start = subparsers.add_parser('start', help="<vmID> Start VM")
parser_start.add_argument('vmID', type=int, help='The (unique) ID of the VM.')

parser_stop = subparsers.add_parser('stop', help='<vmID> Stop VM')
parser_stop.add_argument('vmID', type=int, help='The (unique) ID of the VM.')

parser_reboot = subparsers.add_parser('reboot', help='<vmID> Reboot VM')
parser_reboot.add_argument('vmID', type=int, help='The (unique) ID of the VM.')

parser_console = subparsers.add_parser('console', help="<vmID> Open console vm 'for lxc vm'")
parser_console.add_argument('vmID', type=int, help='The (unique) ID of the VM.')

parser_destroy = subparsers.add_parser('destroy',
                                       help="<vmID> [OPTION] Destroy the container (also delete all uses files).")
parser_destroy.add_argument('vmID', type=int, help='The (unique) ID of the VM.')
parser_destroy.add_argument('-p', '-purge', action="store_true", dest='PURGE',
                            help='Remove container from all related configurations.')

parser_clone = subparsers.add_parser('clone', help="<vmID> <newID> [OPTION] Create a container clone/copy")
parser_clone.add_argument('vmID', type=int, help='The (unique) ID of the VM.')
parser_clone.add_argument('newID', type=int, help='vmID for the clone.')
parser_clone.add_argument('-bwlimit', type=int, help='Override I/O bandwidth limit (in KiB/s).')
parser_clone.add_argument('-description', type=str, help='Description for the new CT/VM.')
parser_clone.add_argument('-full', action="store_true",
                          help='Create a full copy of all disks. This is always done when you clone a normal CT/VM.'
                               'For CT templates, we try to create a linked clone by default.')
parser_clone.add_argument('-name', type=str, help='Set a hostname/name for the new CT/VM.')
parser_clone.add_argument('-pool', type=str, help='Add the new CT to the specified pool.')
parser_clone.add_argument('-snapname', type=str, help='The name of the snapshot.')
parser_clone.add_argument('-storage', type=str, help='Target storage for full clone.')
parser_clone.add_argument('-target', type=str,
                          help='Target node. Only allowed if the original VM is on shared storage.')
parser_clone.add_argument('-format', choices=['qcow2', 'raw', 'vmdk'],
                          help='Target format for file storage. Only valid for full clone. (Only QEMU VM)')

group = parser.add_mutually_exclusive_group()
group.add_argument('-v', '--version', action='version', version=Color.GREEN + version + Color.DEFAULT)

args = parser.parse_args()

# ? Class ----------------------------------------------------------------------------------------->

class Sys:

    def clear():
        _ = system('clear')

    def exit():
        raise SystemExit(0)


class Vm:
    __vm_list = []

    def __init__(self):

        list_pct = os.popen("pct list", "r").read()
        list_qm = os.popen("qm list", "r").read()

        ###############
        # VM LXC LIST #
        ###############

        for line in list_pct.split("\n"):

            if line != "":

                num = int(1)
                temp_dict = {'vm_ID': '', 'Status': '', 'Tag': '', 'Name': ''}

                for string in line.split(" "):

                    if string != "" and string != "VMID" and string != "Status" and string != "Lock" and string != "Name":

                        if num == 1:
                            temp_dict['vm_ID'] = string

                        elif num == 2:
                            temp_dict['Status'] = string

                        elif num == 3:
                            temp_dict['Name'] = string
                            temp_dict['Tag'] = "LXC"

                        num += 1
                
                if temp_dict['vm_ID'] != "":
                    self.__vm_list.append(temp_dict)

        ################
        # VM QEMU LIST #
        ################

        for line in list_qm.split("\n"):
            
            if line != "":

                num = int(1)
                temp_dict = {'vm_ID': '', 'Status': '', 'Tag': '', 'Name': ''}

                for string in line.split(" "):

                    if string != "" and string != "VMID" and string != "STATUS" and string != "NAME" and string != "MEM(MB)" and string != "BOOTDISK(GB)" and string != "PID":

                        if num == 1:
                            temp_dict['vm_ID'] = string

                        elif num == 2:
                            temp_dict['Name'] = string

                        elif num == 3:
                            temp_dict['Status'] = string
                            temp_dict['Tag'] = "QM"

                        num += 1
                
                if temp_dict['vm_ID'] != "":
                    self.__vm_list.append(temp_dict)

    def __check_ID(self, ID_vm):

        if 100 <= int(ID_vm) <= 999:
            return ID_vm

        print(Color.RED + str(ID_vm) + ' ID incorect' + Color.RESET)
        Sys.exit()

    def used_ID(self, ID_vm):

        self.__check_ID(ID_vm)

        for vm_dict in self.__vm_list:
            for value in vm_dict.values():
                if value == str(ID_vm):
                    print(Color.ORANGE + 'The ID "' + str(ID_vm) + '" is already used by another VM' + Color.RESET)
                    Sys.exit()

    def search(self, ID_vm):

        self.__check_ID(ID_vm)

        for vm_dict in self.__vm_list:
            for value in vm_dict.values():
                if value == str(ID_vm):
                    return vm_dict

        print(Color.RED + "No existing VM" + Color.RESET)
        Sys.exit()

    def get_VM_List(self):
        return self.__vm_list


# ? Function ----------------------------------------------------------------------------------------->

def start_VM(info_vm):
    if info_vm["Status"] == "running":
        print(
            Color.MAGENTA + "VM Already " + Color.GREEN + "started " + Color.MAGENTA + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)

    elif info_vm["Tag"] == "LXC":
        print(Color.YELLOW + "Start Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.DEFAULT)
        os.system('pct start ' + str(info_vm["vm_ID"]))
        print(Color.GREEN + "Started Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)

    elif info_vm["Tag"] == "QM":
        print(Color.YELLOW + "Start VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.DEFAULT)
        os.system('qm start ' + str(info_vm["vm_ID"]))
        print(Color.GREEN + "Started VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)


def stop_VM(info_vm):
    if info_vm["Status"] == "stopped":
        print(Color.MAGENTA + "VM Already " + Color.RED + "stopped " + Color.MAGENTA + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)

    elif info_vm["Tag"] == "LXC":
        print(Color.YELLOW + "Stop Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.DEFAULT)
        os.system('pct stop ' + str(info_vm["vm_ID"]))
        print(Color.GREEN + "Stopped Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)

    elif info_vm["Tag"] == "QM":
        print(Color.YELLOW + "Stop VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.DEFAULT)
        os.system('qm stop ' + str(info_vm["vm_ID"]))
        print(Color.GREEN + "Stopped VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)


def reboot_VM(info_vm):
    if info_vm["Status"] == "stopped":
        print(Color.MAGENTA + "The VM is " + Color.RED + "stopped " + Color.MAGENTA + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)

    elif info_vm["Tag"] == "LXC":
        print(Color.YELLOW + "Reboot Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.DEFAULT)
        os.system('pct reboot ' + str(info_vm["vm_ID"]))
        print(Color.GREEN + "Rebooted Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)

    elif info_vm["Tag"] == "QM":
        print(Color.YELLOW + "Reboot VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.DEFAULT)
        os.system('qm reboot ' + str(info_vm["vm_ID"]))
        print(Color.GREEN + "Rebooted VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)


def console_VM(info_vm):
    if info_vm["Status"] == "stopped":
        print(Color.MAGENTA + "The VM is " + Color.RED + "stopped " + Color.MAGENTA + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)

    elif info_vm["Tag"] == "LXC":
        print(Color.YELLOW + "exit the console Ctrl+a q" + Color.Reset)
        os.system('pct console ' + str(info_vm["vm_ID"]) + ' -escape ^a')
        Sys.clear()

    elif info_vm["Tag"] == "QM":
        print(Color.YELLOW + "use 'qm terminal' and config serial" + Color.RESET)


def destroy_VM(info_vm, opti=""):
    if info_vm["Status"] == "running":
        print(
            Color.MAGENTA + "The VM is " + Color.GREEN + "running " + Color.MAGENTA + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)
        Sys.exit()

    choicer_Action = input(Color.ORANGE + "Do you really want to remove the VM : " + Color.UNDERLINE + Color.CYAN + info_vm[
        "Name"] + Color.DEFAULT + " (" + Color.GREEN + "Y" + Color.DEFAULT + "/" + Color.RED + "[N]" + Color.DEFAULT + "): ")
    print()

    if choicer_Action == 'Y' or choicer_Action == 'y':

        input_vmID = input(Color.MAGENTA + "Please enter the ID to confirm" + Color.DEFAULT + " (" + info_vm["vm_ID"] + ") : ")

        if input_vmID == info_vm["vm_ID"]:
            print(Color.Reset)
            if info_vm["Tag"] == "LXC":
                os.system('pct destroy ' + str(info_vm["vm_ID"]) + opti)

            elif info_vm["Tag"] == "QM":
                os.system('qm destroy ' + str(info_vm["vm_ID"]) + opti)
        else:
            print(Color.RED + 'Wrong ID : ' + input_vmID + Color.RESET)
            Sys.exit()

        print()

    else:
        print()
        Sys.exit()


def clone_VM(info_vm, new_vm, opti=""):
    if info_vm["Status"] == "running":
        print(
            Color.MAGENTA + "The VM is " + Color.GREEN + "running " + Color.MAGENTA + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)
        Sys.exit()

    if info_vm["Tag"] == "LXC":
        print()
        os.system('pct clone ' + str(info_vm["vm_ID"]) + ' ' + str(new_vm) + opti)

    elif info_vm["Tag"] == "QM":
        print()
        os.system('qm clone ' + str(info_vm["vm_ID"]) + ' ' + str(new_vm) + opti)

    print()
    Sys.exit()

# ? Start ----------------------------------------------------------------------------------------->

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
    if args.PURGE: option = " -purge "
    destroy_VM(vm_info, option)
    Sys.exit()

if args.Command_Name == 'clone':

    vm.used_ID(args.newID)
    vm_info = vm.search(args.vmID)

    if args.bwlimit: option += " -bwlimit " + str(args.bwlimit)
    if args.description: option += " -description " + str(args.description)
    if args.full: option += " -full"
    if args.pool: option += " -pool " + str(args.pool)
    if args.snapname: option += " -snapname " + str(args.snapname)
    if args.storage: option += " -storage " + str(args.storage)
    if args.target: option += " -target " + str(args.target)
    if args.name:  #▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        if vm_info["Tag"] == "LXC":
            option += " -hostname " + args.name
        elif vm_info["Tag"] == "QM":
            option += " -name " + args.name
    if args.format:  #▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        if vm_info["Tag"] == "QM":
            option += " -format " + args.format
        else:
            print(Color.ORANGE + 'The "-format" option is only available for VM (QEMU)' + Color.RESET)
            Sys.exit()

    clone_VM(vm_info, args.newID, option)
    Sys.exit()

if args.Command_Name == 'list':

    key_sort = 'vm_ID'

    if args.sort:
        if args.sort == "type": key_sort = 'Tag'
        elif args.sort == "status": key_sort = 'Status'
        elif args.sort == "name": key_sort = 'Name'

    Sys.clear()
    print("\n")

    vm_list_sort = sorted(vm.get_VM_List(), key=itemgetter(key_sort), reverse=args.REVERSE)

    form_header = "{0:6}{1:10}{2:6}{3:10}"
    form_Stop = "{0:6}" + Color.RED + "{1:10}" + Color.DEFAULT + "{2:6}{3:10}"
    form_Start = "{0:6}" + Color.GREEN + "{1:10}" + Color.DEFAULT + "{2:6}{3:10}"
    dash = '-' * 40
    title = ['VMID', 'Status', 'Type', 'Name']

    print(dash)
    print(form_header.format(*title))
    print(dash)

    for vm_dict in vm_list_sort:
        
        vm_print = list(vm_dict.values())

        if vm_print[1] == 'stopped':
            print(form_Stop.format(*vm_print))
        elif vm_print[1] == 'running':
            print(form_Start.format(*vm_print))

    print(Color.RESET)

    Sys.exit()

print(Color.RED + 'No argument detected' + Color.RESET)

parser.print_help()

print('\n')