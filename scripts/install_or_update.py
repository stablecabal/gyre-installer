import hashlib
from os import path
import os, subprocess, shutil, re, sys, time

from lib.colorama import  just_fix_windows_console, Fore, Style
just_fix_windows_console()

from lib import pynvml

GB = 1024 * 1024 * 1024

def check_environment(hf_cache_home):
    pynvml.nvmlInit()

    has_warning = False

    def error(str):
        print(Fore.RED, "\n----Error--------------------------")
        print(str)
        print("-----------------------------------", Style.RESET_ALL)
        sys.exit(-1)

    def warning(str):
        nonlocal has_warning
        has_warning = True
        print(Fore.YELLOW, "\n----Warning--------------------------")
        print(str)
        print("-------------------------------------", Style.RESET_ALL)

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

    return has_warning

def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, "rb", buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()


def main():
    base=path.dirname(path.dirname(path.abspath(__file__)))

    # Create config if it doesn't exist
    
    if not path.exists(path.join(base, "config")):
        shutil.copy(path.join(base, "config.dist"), path.join(base, "config"))

    # Read the config

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

    # We can't rely on dotenv existing yet, stdlib only
    with open(path.join(base, "config"), "r") as config_file:
        for line in config_file:
            repo_match = re.match(r'\s*AIO_REPO\s*=\s*(\S+)', line)
            branch_match = re.match(r'\s*AIO_BRANCH\s*=\s*(\S+)', line)
            home_match = re.match(r'\s*HF_HOME\s*=\s*(\S+)', line)

            if repo_match: repo=repo_match.group(1)
            if branch_match: branch=branch_match.group(1)
            if home_match: hf_cache_home=os.path.abspath(home_match.group(1))

    # Run a basic environment check before doing anything
    if check_environment(hf_cache_home):
        print("(Continuing in 5 seconds....)", flush=True)
        time.sleep(5)

    # Update this repo, and any submodules

    if not path.exists(path.join(base, ".git")):
        subprocess.run(("git", "init"), cwd=base)

    result = subprocess.run(("git", "remote", "get-url", "origin"), cwd=base, capture_output=True, text=True)
    has_remote = result.returncode == 0
    remote_url = result.stdout.strip()

    if not has_remote:
        subprocess.run(("git", "remote", "add", "origin", repo), cwd=base)
    elif remote_url != repo:
        subprocess.run(("git", "remote", "set-url", "origin", repo), cwd=base)

    existing_selfhash = sha256sum(__file__)

    subprocess.run(("git", "fetch"), cwd=base)
    subprocess.run(("git", "reset", "--hard", "origin/"+branch), cwd=base)
    subprocess.run(("git", "submodule", "update", "--init", "--recursive"), cwd=base)

    new_selfhash = sha256sum(__file__)
    if existing_selfhash != new_selfhash:
        if len(sys.argv) > 1 and sys.argv[1] == "dont_restart":
            print("Installer updated, but not restarting to avoid infinite loop. Please manually re-run.")
            return
        
        print("Installer updated. Restarting.\n\n", flush=True)
        subprocess.run(("python", os.path.realpath(__file__), "dont_restart"), cwd=base)
        return

    # Install the server dependencies

    os.environ["PIP_EXTRA_INDEX_URL"]="https://download.pytorch.org/whl/cu116"
    os.environ["PIP_FIND_LINKS"]="https://download.openmmlab.com/mmcv/dist/cu116/torch1.12/index.html"
    subprocess.run(("python", "-m", "flit", "install", "--pth-file"), cwd=os.path.join(base, "gyre"))

    # Install xformers
    if sys.platform.startswith("win"):
        xformers_url = open(path.join(base, ".xformers_url"), "r").read().strip()
        subprocess.run(("pip", "install", xformers_url), cwd=base)

if __name__ == "__main__":
    main()