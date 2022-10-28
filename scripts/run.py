from os import path
import subprocess, os, shutil, sys
from dotenv import load_dotenv

def main():
    base=path.dirname(path.dirname(__file__))

    # Load dotenv into environment

    load_dotenv(path.join(base, "config"))
    
    hfToken = os.environ.get('HF_API_TOKEN', '')
    if not hfToken or hfToken == '{your huggingface token}':
        print("ERROR: You need to register an account on HuggingFace, create an API token, and save it into the 'config' file in this directory")
        input("Press enter to exit")
        sys.exit(-1)
    if hfToken[0] == "{":
        print("ERROR: Don't wrap your token with {} brackets.")
        input("Press enter to exit")
        sys.exit(-1)

    # Run server

    os.environ["SD_HTTP_FILE_ROOT"] = path.join(base, "idea2art")

    from sdgrpcserver import server
    server.main()
    
if __name__ == "__main__":
    main()