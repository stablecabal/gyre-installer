from os import path
import os, subprocess, shutil, re, sys

def main():
    base=path.dirname(path.dirname(path.abspath(__file__)))

    # Create config if it doesn't exist
    
    if not path.exists(path.join(base, "config")):
        shutil.copy(path.join(base, "config.dist"), path.join(base, "config"))

    # Read the config

    repo = os.environ.get("AIO_REPO", "https://github.com/stablecabal/gyre-installer.git")
    branch = os.environ.get("AIO_BRANCH", "main") 

    # We can't rely on dotenv existing yet, stdlib only
    with open(path.join(base, "config"), "r") as config_file:
        for line in config_file:
            repo_match = re.match(r'\s*AIO_REPO=(\S+)', line)
            branch_match = re.match(r'\s*AIO_BRANCH\s*=\s*(\S+)', line)

            if repo_match: repo=repo_match.group(1)
            if branch_match: branch=branch_match.group(1)

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

    subprocess.run(("git", "fetch"), cwd=base)
    subprocess.run(("git", "reset", "--hard", "origin/"+branch), cwd=base)
    subprocess.run(("git", "submodule", "update", "--init", "--recursive"), cwd=base)
    
    # Install the server dependencies

    os.environ["PIP_EXTRA_INDEX_URL"]="https://download.pytorch.org/whl/cu116"
    subprocess.run(("python", "-m", "flit", "install", "--pth-file"), cwd=os.path.join(base, "gyre"))

    # Install xformers
    if sys.platform.startswith("win"):
        xformers_url = open(path.join(base, ".xformers_url"), "r").read().strip()
        subprocess.run(("pip", "install", xformers_url), cwd=base)

if __name__ == "__main__":
    main()