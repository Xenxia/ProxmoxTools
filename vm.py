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

version = "2.0.0"


# ? Color ------------------------------------------------------------------------------->
class Co:
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
parser = argparse.ArgumentParser(description="Application to merge the 'qm' and 'pct' commands from proxmox",
                                 allow_abbrev=False,
                                 prog='vm',
                                 usage="%(prog)s"
                                 )

subparsers = parser.add_subparsers(title='Commande',
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

parser_destroy = subparsers.add_parser('destroy',
                                       help="<vmID> [OPTION] Destroy the container (also delete all uses files).")
parser_destroy.add_argument('vmID', type=int, help='The (unique) ID of the VM.')
parser_destroy.add_argument('-p', '-purge', action="store_true", dest='Purge',
                            help='Remove container from all related configurations.')

parser_clone = subparsers.add_parser('clone', help="<vmID> <newID> [OPTION] Create a container clone/copy")
parser_clone.add_argument('vmID', type=int, help='The (unique) ID of the VM.')
parser_clone.add_argument('newID', type=int, help='vmID for the clone.')
parser_clone.add_argument('-bwlimit', type=int, help='Override I/O bandwidth limit (in KiB/s).')
parser_clone.add_argument('-description', type=str, help='Description for the new CT/VM.')
parser_clone.add_argument('-full', action="store_true",
                          help='Create a full copy of all disks. This is always done when you clone a normal CT/VM. '
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
group.add_argument('-v', '--version', action='version', version=Co.GREEN + version + Co.DEFAULT)
group.add_argument("-l", "--list", action="store_true", help="shows the list of all VMs")

args = parser.parse_args()


# ? Class ----------------------------------------------------------------------------------------->

class Sys:

    @staticmethod
    def clear():
        _ = system('clear')

    def exit(self):
        raise SystemExit(0)


class Vm:
    __vm_dict = {}

    def __init__(self):

        self.__vm_dict[0] = {'#1': 'VMID', '#2': 'Status', '#3': 'Type', '#4': 'Name'}
        list_pct = os.popen("pct list", "r").read()
        list_qm = os.popen("qm list", "r").read()
        num_dict = int(1)

        ###############
        # VM LXC LIST #
        ###############

        for line in list_pct.split("\n"):
            num = int(1)
            self.__vm_dict[num_dict] = {'vm_ID': '', 'Status': '', 'Tag': '', 'Name': ''}

            for string in line.split(" "):

                if string != "" and string != "VMID" and string != "Status" and string != "Lock" and string != "Name":

                    if num == 1:
                        self.__vm_dict[num_dict]['vm_ID'] = string

                    if num == 2:
                        self.__vm_dict[num_dict]['Status'] = string

                    if num == 3:
                        self.__vm_dict[num_dict]['Name'] = string
                        self.__vm_dict[num_dict]['Tag'] = "LXC"
                        num_dict += 1

                    num += 1

        ################
        # VM QEMU LIST #
        ################

        for line in list_qm.split("\n"):
            num = int(1)
            self.__vm_dict[num_dict] = {'vm_ID': '', 'Status': '', 'Tag': '', 'Name': ''}

            for string in line.split(" "):

                if string != "" and string != "VMID" and string != "STATUS" and string != "NAME" and string != "MEM(MB)" and string != "BOOTDISK(GB)" and string != "PID":

                    if num == 1:
                        self.__vm_dict[num_dict]['vm_ID'] = string

                    if num == 2:
                        self.__vm_dict[num_dict]['Name'] = string

                    if num == 3:
                        self.__vm_dict[num_dict]['Status'] = string
                        self.__vm_dict[num_dict]['Tag'] = "QM"
                        num_dict += 1

                    num += 1

    @staticmethod
    def __check_ID(ID_vm):
        if 100 <= int(ID_vm) <= 999:
            return ID_vm

        print(Co.RED + str(ID_vm) + ' ID incorect' + Co.RESET)
        Sys.exit()

    def used_ID(self, ID_vm):
        self.__check_ID(ID_vm)
        num_total_vm = len(self.__vm_dict)

        for num_dict in range(1, num_total_vm):
            for value in self.__vm_dict[num_dict].values():
                if value == str(ID_vm):
                    print(Co.ORANGE + 'The ID "' + str(ID_vm) + '" is already used by another VM' + Co.RESET)
                    Sys.exit()

    def search(self, ID_vm):
        self.__check_ID(ID_vm)
        num_total_vm = len(self.__vm_dict)

        for num_dict in range(1, num_total_vm):
            for value in self.__vm_dict[num_dict].values():
                if value == str(ID_vm):
                    return self.__vm_dict[num_dict]

        print(Co.RED + "No existing VM" + Co.RESET)
        Sys.exit()

    def getDico(self):
        return self.__vm_dict


# ? Function ----------------------------------------------------------------------------------------->
def start_VM(info_vm):
    if info_vm["Status"] == "running":
        print(
            Co.MAGENTA + "VM Already " + Co.GREEN + "started " + Co.MAGENTA + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.RESET)

    elif info_vm["Tag"] == "LXC":
        print(Co.YELLOW + "Start Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.DEFAULT)
        os.system('pct start ' + str(info_vm["vm_ID"]))
        print(Co.GREEN + "Started Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.RESET)

    elif info_vm["Tag"] == "QM":
        print(Co.YELLOW + "Start VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.DEFAULT)
        os.system('qm start ' + str(info_vm["vm_ID"]))
        print(Co.GREEN + "Started VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.RESET)


def stop_VM(info_vm):
    if info_vm["Status"] == "stopped":
        print(Co.MAGENTA + "VM Already " + Co.RED + "stopped " + Co.MAGENTA + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.RESET)

    elif info_vm["Tag"] == "LXC":
        print(Co.YELLOW + "Stop Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.DEFAULT)
        os.system('pct stop ' + str(info_vm["vm_ID"]))
        print(Co.GREEN + "Stopped Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.RESET)

    elif info_vm["Tag"] == "QM":
        print(Co.YELLOW + "Stop VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.DEFAULT)
        os.system('qm stop ' + str(info_vm["vm_ID"]))
        print(Co.GREEN + "Stopped VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.RESET)


def reboot_VM(info_vm):
    if info_vm["Status"] == "stopped":
        print(Co.MAGENTA + "The VM is " + Co.RED + "stopped " + Co.MAGENTA + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.RESET)

    elif info_vm["Tag"] == "LXC":
        print(Co.YELLOW + "Reboot Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.DEFAULT)
        os.system('pct reboot ' + str(info_vm["vm_ID"]))
        print(Co.GREEN + "Rebooted Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.RESET)

    elif info_vm["Tag"] == "QM":
        print(Co.YELLOW + "Reboot VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.DEFAULT)
        os.system('qm reboot ' + str(info_vm["vm_ID"]))
        print(Co.GREEN + "Rebooted VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.RESET)


def console_VM(info_vm):
    if info_vm["Status"] == "stopped":
        print(Co.MAGENTA + "The VM is " + Co.RED + "stopped " + Co.MAGENTA + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.RESET)

    elif info_vm["Tag"] == "LXC":
        print(Co.YELLOW + "exit the console Ctrl+a q" + Co.Reset)
        os.system('pct console ' + str(info_vm["vm_ID"]) + ' -escape ^a')
        Sys.clear()

    elif info_vm["Tag"] == "QM":
        print(Co.YELLOW + "use 'qm terminal' and config serial" + Co.RESET)


def destroy_VM(info_vm, opti=""):
    if info_vm["Status"] == "running":
        print(
            Co.MAGENTA + "The VM is " + Co.GREEN + "running " + Co.MAGENTA + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.RESET)
        Sys.exit()

    choicer_Action = input(Co.ORANGE + "Do you really want to remove the VM : " + Co.UNDERLINE + Co.CYAN + info_vm[
        "Name"] + Co.DEFAULT + " (" + Co.GREEN + "Y" + Co.DEFAULT + "/" + Co.RED + "[N]" + Co.DEFAULT + "): ")
    print()

    if choicer_Action == 'Y' or choicer_Action == 'y':

        input_vmID = input(Co.MAGENTA + "Please enter the ID to confirm" + Co.DEFAULT + " (" + info_vm["vm_ID"] + ") : ")

        if input_vmID == info_vm["vm_ID"]:
            print(Co.Reset)
            if info_vm["Tag"] == "LXC":
                os.system('pct destroy ' + str(info_vm["vm_ID"]) + opti)

            elif info_vm["Tag"] == "QM":
                os.system('qm destroy ' + str(info_vm["vm_ID"]) + opti)
        else:
            print(Co.RED + 'Wrong ID : ' + input_vmID + Co.RESET)
            Sys.exit()

        print()

    else:
        print()
        Sys.exit()


def clone_VM(info_vm, new_vm, opti=""):
    if info_vm["Status"] == "running":
        print(
            Co.MAGENTA + "The VM is " + Co.GREEN + "running " + Co.MAGENTA + info_vm["Name"] + ':' + info_vm["vm_ID"] + Co.RESET)
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
    if args.Purge: option = " -purge "
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
    if args.name:  # -------------------------->
        if vm_info["Tag"] == "LXC":
            option += " -hostname " + args.name
        elif vm_info["Tag"] == "QM":
            option += " -name " + args.name
    if args.format:  # -------------------------->
        if vm_info["Tag"] == "QM":
            option += " -format " + args.format
        else:
            print(Co.ORANGE + 'The "-format" option is only available for VM (QEMU)' + Co.RESET)
            Sys.exit()

    clone_VM(vm_info, args.newID, option)
    Sys.exit()

if args.list:

    Sys.clear()
    print("\n")

    vm_dict = vm.getDico()

    num_vm_len = len(vm_dict)

    form_header = "{0:6}{1:10}{2:6}{3:10}"
    form_Stop = "{0:6}" + Co.RED + "{1:10}" + Co.DEFAULT + "{2:6}{3:10}"
    form_Start = "{0:6}" + Co.GREEN + "{1:10}" + Co.DEFAULT + "{2:6}{3:10}"
    dash = '-' * 40

    for x in range(0, num_vm_len - 1):

        vm_print = list(vm_dict[x].values())

        if x != 0:
            if vm_print[1] == 'stopped':
                print(form_Stop.format(*vm_print))
            elif vm_print[1] == 'running':
                print(form_Start.format(*vm_print))
        else:
            print(dash)
            print(form_header.format(*vm_print))
            print(dash)

    print(Co.RESET)

    Sys.exit()

print(Co.RED + 'No argument detected' + Co.RESET)

parser.print_help()

print('\n')