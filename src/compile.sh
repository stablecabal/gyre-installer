#!/bin/bash

# This depends on my specific setup:
#   - "dart" runs the linux version of dart (in WSL)
#   - "dart.bat" in a cmd.exe environment runs the windows version of dart
#   - the code is usually on my WSL drive

# -- Linux

dart pub get
dart compile exe -o ../bin/install_or_update-Linux install_or_update.dart

# -- Windows

mkdir -p ~/winhome/work/gi_tmp
cp pubspec.* *.dart ~/winhome/work/gi_tmp
pushd ~/winhome/work/gi_tmp
cmd.exe /c dart.bat pub get
cmd.exe /c dart.bat compile exe -o install_or_update.exe install_or_update.dart
popd
mv  ~/winhome/work/gi_tmp/install_or_update.exe ../bin/


