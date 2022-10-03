@echo off
if not exist "env\" .\micromamba\micromamba.exe -r env -y create -f environment.yaml
copy .\micromamba\micromamba.exe env
.\env\micromamba.exe -r env -y update -f environment.yaml
.\env\micromamba.exe -r env -n sd-grpc-server run python ./scripts/install_or_update.py
