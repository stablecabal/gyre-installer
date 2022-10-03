from os import path
import subprocess, os, shutil
from dotenv import load_dotenv
from sdgrpcserver import server

def main():
    base=path.dirname(path.dirname(__file__))

    # Load dotenv into environment

    load_dotenv(path.join(base, "config"))

    # Run server

    server.main({
        "http_root": path.join(base, "idea2art"),
        "http_port": 8000
    })
    
if __name__ == "__main__":
    main()