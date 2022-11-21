@echo off

rem Detect conda, or use micromamba if it doesn't exist
if [%CONDA_EXE%] EQU [] (
    set MAMBA_ROOT_PREFIX=%~dp0env
    set SDCONDA_EXE=%~dp0env\micromamba.exe
    if not exist %SDCONDA_EXE% (
        mkdir env
        copy .\micromamba\micromamba.exe env
    )
) else (
    set SDCONDA_EXE=%CONDA_EXE%
)

rem Test if environment exists at all
"%SDCONDA_EXE%" -n sd-grpc-server -q run rem >NUL 2>NUL

rem Create or update environment
if %ERRORLEVEL% NEQ 0 (
    "%SDCONDA_EXE%" -y create -f environment.yaml
) else (
    "%SDCONDA_EXE%" -y update -f environment.yaml
)

rem And use python to handle the rest of the install/update process
"%SDCONDA_EXE%" -n sd-grpc-server run python ./scripts/install_or_update.py
