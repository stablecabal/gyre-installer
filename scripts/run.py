from os import path
import subprocess, os, shutil, sys
from dotenv import load_dotenv
from sdgrpcserver import server

def main():
    base=path.dirname(path.dirname(__file__))

    # Load dotenv into environment

    load_dotenv(path.join(base, "config"))
    
    hfToken = os.environ.get('HF_API_TOKEN', '')
    if not hfToken or hfToken == '{your huggingface token}':
        print("You need to register an account on HuggingFace, create an API token, and save it into the 'config' file in this directory")
        sys.exit(-1)

    # Run server

    os.environ["SD_HTTP_FILE_ROOT"] = path.join(base, "idea2art")
    server.main()
    
if __name__ == "__main__":
    main()