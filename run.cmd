@echo off
start .\env\micromamba.exe -r env -n sd-grpc-server run python ./scripts/run.py

