from os import path
import subprocess, os, shutil, sys
from dotenv import load_dotenv

def main():
    base=path.dirname(path.dirname(path.abspath(__file__)))

    # Load dotenv into environment

    load_dotenv(path.join(base, "config"))

    # If idea2art is included, configure server to use it

    idea2art_path = path.join(base, "idea2art")
    if path.isdir(idea2art_path):
        print ("Idea2.art enabled")
        os.environ["SD_HTTP_FILE_ROOT"] = idea2art_path

    # Run server

    from gyre import server
    server.main()
    
if __name__ == "__main__":
    main()