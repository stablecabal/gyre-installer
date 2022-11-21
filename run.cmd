@echo off

rem Detect conda, or use micromamba if it doesn't exist
if [%CONDA_EXE%] EQU [] (
    set MAMBA_ROOT_PREFIX=%~dp0env
    set SDCONDA_EXE=%~dp0env\micromamba.exe
) else (
    set SDCONDA_EXE=%CONDA_EXE%
)

rem Use python to handle the rest of the run process
"%SDCONDA_EXE%" -n sd-grpc-server run python ./scripts/run.py

