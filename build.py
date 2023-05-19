import argparse
import os, pathlib, shutil, json, platform
import PyInstaller.__main__
import compileall

PLATFORM_SYS = platform.system()

CONFIG_FILE = "build.json"

CONFIG_TEMPLATE = '''
{   
    // Name App
    "name_app": "",

    // Entry script
    "index": "",

    // Icon App
    "icon": "",

    // Build on one file
    "onefile": true,

    // Clean build file
    "clean": false,

    // Contains pre-build scripts for the app
    //Move to: parentDir/comp
    "compile_dir": [],

    // Add File or Dir | img;img (Dir img to Dir img)
    "add_data": [],

    // Import not in entry script
    "hidden_import": []
}
'''
parser = argparse.ArgumentParser(description="app to build",
                                 allow_abbrev=False,
                                 prog='Build',
                                 usage='%(prog)s'
                                 )

subparsers = parser.add_subparsers(title='Commande',
                                   dest='Command_Name',
                                   )

parser_dev = subparsers.add_parser('dev', help='Build app development',
                                    formatter_class=argparse.RawTextHelpFormatter)

parser_dev = subparsers.add_parser('config', help='Générate template config',
                                    formatter_class=argparse.RawTextHelpFormatter)

# parser_prod = subparsers.add_parser('prod', help='Build app production',
#                                     formatter_class=argparse.RawTextHelpFormatter)

group = parser.add_mutually_exclusive_group()
group.add_argument('-v', '--version', action='version', version="V1")

args = parser.parse_args()

#load file config

with open(CONFIG_FILE, 'r', encoding='utf8') as file:
    config = json.load(file)

if config["compile_dir"] != []:
    for path in config["compile_dir"]:

        compileall.compile_dir(dir=path, legacy=True, force=True)

        path_comp = f"./{path}/comp"
        if os.path.exists(path_comp):
            shutil.rmtree(path_comp)
        os.mkdir(path_comp)
        for file in pathlib.Path(f"./{path}").glob("*.pyc"):
            os.rename(str(file), f"{path_comp}/{file.name}")

if args.Command_Name == "dev":

    arg_dev = [
        config["index"],
        f"--name={config['name_app']}_dev",
    ]

    if config["onefile"]: arg_dev.append("--onefile")
    if config["clean"]: arg_dev.append("--clean")
    if config["icon"] != "": arg_dev.append(f"--icon={config['icon']}")

    if config["add_data"] != []:
        for i in config["add_data"]:
            arg_dev.append(f"--add-data={i}")

    if config["hidden_import"] != []:
        for i in config["hidden_import"]:
            arg_dev.append(f"--hidden-import={i}")

    print("\n=========================================== BUILD DEV ===========================================\n")
    PyInstaller.__main__.run(arg_dev)
    print("\n========================================= END BUILD DEV ==========================================\n")

else:

    arg = [
        config["index"],
        f"--name={config['name_app']}",
    ]

    if PLATFORM_SYS == "Windows":
        arg.append("--windowed")

    if config["onefile"]: arg.append("--onefile")
    if config["clean"]: arg.append("--clean")
    if config["icon"] != "": arg.append(f"--icon={config['icon']}")

    if config["add_data"] != []:
        for i in config["add_data"]:
            arg.append(f"--add-data={i}")

    if config["hidden_import"] != []:
        for i in config["hidden_import"]:
            arg.append(f"--hidden-import={i}")

    print("=========================================== BUILD PROD ===========================================\n")
    PyInstaller.__main__.run(arg)
    print("\n========================================= END BUILD PROD ==========================================\n")

if args.Command_Name == "config":
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(CONFIG_TEMPLATE, f)
