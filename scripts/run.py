from os import path
import subprocess, os, shutil, sys
from dotenv import load_dotenv

def main():
    base=path.dirname(path.dirname(__file__))

    # Load dotenv into environment

    load_dotenv(path.join(base, "config"))
    
    # Run server

    os.environ["SD_HTTP_FILE_ROOT"] = path.join(base, "idea2art")

    from gyre import server
    server.main()
    
if __name__ == "__main__":
    main()