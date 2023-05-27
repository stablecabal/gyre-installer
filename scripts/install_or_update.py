import hashlib
from os import path
import os, subprocess, shutil, re, sys, time

from lib.colorama import  just_fix_windows_console, Fore, Style
just_fix_windows_console()

from lib import pynvml

GB = 1024 * 1024 * 1024

has_warning = False

def error(str):
    print(Fore.RED, "\n----Error--------------------------")
    print(str)
    print("-----------------------------------", Style.RESET_ALL)
    sys.exit(-1)

def warning(str):
    global has_warning
    has_warning = True
    print(Fore.YELLOW, "\n----Warning--------------------------")
    print(str)
    print("-------------------------------------", Style.RESET_ALL)

def check_environment(hf_cache_home):
    pynvml.nvmlInit()

    try:
        # Find a pynvml card

        count = 0
        try:
            count = pynvml.nvmlDeviceGetCount()
        except pynvml.NVMLError as error:
            print(error)

        if count == 0:
            error("Could not find any Nvidia cards. Gyre requires a recent NVidia card.")
            sys.exit(-1)

        # Check max ram and arch

        max_ram = 0
        max_arch = 0
        for i in range(count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            max_ram = max(max_ram, info.total)
            max_arch = max(max_arch, pynvml.nvmlDeviceGetArchitecture(handle))

        if max_ram < 3.9*GB:
            warning("Could not find an NVidia card with at least 4GB RAM.\nYou can still try and use Gyre, but some functions may fail.")

        if max_arch < pynvml.NVML_DEVICE_ARCH_PASCAL:
            warning("Could not find an Nvidia card with at least the Pascal architecture (10xx).\nGyre probably won't work.")
        elif max_arch < pynvml.NVML_DEVICE_ARCH_TURING:
            warning("Could not find an Nvidia card with at least the Turing architecture (20xx).\nGyre should work, but you might run into some issues.")

        # Check disk space
        os.makedirs(hf_cache_home, exist_ok=True)
        usage = shutil.disk_usage(hf_cache_home)

        if usage.free < 40 * GB:
            warning(f"Less than 40GB free for Huggingface Cache at {hf_cache_home}.\nIf you haven't downloaded the models yet, you will need to free more drive space before running run.cmd.")

    finally:
        pynvml.nvmlShutdown()

def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, "rb", buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()

# We can't rely on dotenv existing yet, stdlib only
def parse_dotenv(filename, rv = None):
    if rv is None:
        rv = {}

    with open(filename, "r") as config_file:
        for line in config_file:
            if line_match := re.match(r'\s*([^\s=]+)\s*=\s*(.+)', line):
                rv[line_match.group(1)] = line_match.group(2)
    
    return rv

def create_initial_config():
    base=path.dirname(path.dirname(path.abspath(__file__)))
    default_home=os.path.join(os.path.expanduser("~"), ".cache")
    config = parse_dotenv(path.join(base, "config.dist"))

    override_path = None
    override_branch = None

    # -- Ask client if they want to override the path

    while override_path is None:
        print("")
        print("Where would you like to store downloaded models:")
        print(f"  1: [Default] The default huggingface cache (normally {default_home})")
        print("  2: A custom path")
        print("")
        user_input = input("Enter '1', '2', 'q' to abort, or press enter to use the default: ").strip()

        if user_input == "q":
            print("Aborting install. Run install_or_update.cmd again to continue later.")
            sys.exit(-1)
        elif user_input == "1" or user_input == "" :
            override_path = False
        elif user_input == "2":
            override_path = True

    while override_path is True:
        print("")
        override_path = input("Please enter the custom path (for example, e:/gyremodels): ")
        override_path.strip().replace('\\', '/')

    if override_path:
        print("")
        print("Models will be downloaded into ", override_path)
        print("You can change this path later by editing your config file and manually moving any downloaded models")
        print("", flush=True)

        config["XDG_CACHE_HOME"] = override_path

    # -- Ask client if they want to override the branch

    branch_default = config.get("AIO_BRANCH", "main")

    while override_branch is None:
        print("")
        print("What branch would you like to install?:")
        print("")
        print("  Stable versions:")
        print("  ---------------------")
        print(f"    1: {'[Default] ' if branch_default == 'main' else ''}The gyre server")
        print(f"    2: {'[Default] ' if branch_default == 'bundle' else ''}The gyre + flying dog AI studio bundle")
        print("")
        print("  Test versions (newer features, but more bugs):")
        print("  ---------------------")
        print("    3: The gyre server")
        print("    4: The gyre + flying dog AI studio bundle")
        print("")
        user_input = input("Enter '1', '2', '3', '4', 'q' to abort, or press enter to use the default: ").strip()

        if user_input == "q":
            print("Aborting install. Run install_or_update.cmd again to continue later.")
            sys.exit(-1)
        elif user_input == "":
            override_branch = branch_default
        elif user_input == "1":
            override_branch = "main"
        elif user_input == "2":
            override_branch = "bundle"
        elif user_input == "3":
            override_branch = "test"
        elif user_input == "4":
            override_branch = "bundle-test"

    config["AIO_BRANCH"] = override_branch

    if "bundle" in override_branch:
        config["SD_HTTP_FILE_ROOT"]="./aistudio/dist"
        config["SD_HTTP_PROXY_1"]="flyingdog:www.flyingdog.de"

    with open(path.join(base, "config"), "w") as config_file:
        for k, v in config.items():
            config_file.write(f"{k}={v}\n")

def main():
    base=path.dirname(path.dirname(path.abspath(__file__)))
    default_home=os.path.join(os.path.expanduser("~"), ".cache")

    # Create config if it doesn't exist
    
    if not path.exists(path.join(base, "config")):
        create_initial_config()

    # Read it in

    parse_dotenv(path.join(base, "config"), os.environ)

    # Get some variables from the config

    repo = os.environ.get("AIO_REPO", "https://github.com/stablecabal/gyre-installer.git")
    branch = os.environ.get("AIO_BRANCH", "main") 

    # From huggingface_hub/constants.py

    default_home = os.path.join(os.path.expanduser("~"), ".cache")
    hf_cache_home = os.path.expanduser(
        os.getenv(
            "HF_HOME",
            os.path.join(os.getenv("XDG_CACHE_HOME", default_home), "huggingface"),
        )
    )

    # Run a basic environment check before doing anything

    check_environment(hf_cache_home)
    if has_warning:
        print("(Continuing in 5 seconds....)", flush=True)
        time.sleep(5)

    # Wrapper around subprocess.run that checks returncode and aborts if non-zero

    def run(*args, **kwargs):
        default_kwargs = {"cwd": base}
        default_kwargs.update(kwargs)

        result = subprocess.run(*args, **default_kwargs)
        if result.returncode != 0:
            error("Whoops - something went wrong. Aborting.")


    # Update this repo, and any submodules

    if not path.exists(path.join(base, ".git")):
        run(("git", "init"))

    result = subprocess.run(("git", "remote", "get-url", "origin"), cwd=base, capture_output=True, text=True)
    has_remote = result.returncode == 0
    remote_url = result.stdout.strip()

    if not has_remote:
        run(("git", "remote", "add", "origin", repo))
    elif remote_url != repo:
        run(("git", "remote", "set-url", "origin", repo))

    existing_selfhash = sha256sum(__file__)

    run(("git", "fetch"))
    run(("git", "reset", "--hard", "origin/"+branch))
    run(("git", "submodule", "update", "--init", "--recursive", "--force"))

    new_selfhash = sha256sum(__file__)
    if existing_selfhash != new_selfhash:
        if "dont_restart" in sys.argv:
            print("Installer updated, but not restarting to avoid infinite loop. Please manually re-run.")
            return
        
        print("Installer updated. Restarting.\n\n", flush=True)
        subprocess.run(("python", os.path.realpath(__file__), "dont_restart"), cwd=base)
        return

    # Install the server dependencies

    os.environ["PIP_EXTRA_INDEX_URL"]="https://download.pytorch.org/whl/cu116"
    os.environ["PIP_FIND_LINKS"]="https://download.openmmlab.com/mmcv/dist/cu116/torch1.12/index.html"
    run(("python", "-m", "flit", "install", "--pth-file"), cwd=os.path.join(base, "gyre"))

    # Install xformers
    if sys.platform.startswith("win"):
        xformers_url = open(path.join(base, ".xformers_url"), "r").read().strip()
        run(("pip", "install", xformers_url))

if __name__ == "__main__":
    main()