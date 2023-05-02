import 'package:path/path.dart' as p;
import 'dart:io';

void main() async {
  final script = Platform.script.toFilePath();

  var root = p.dirname(script);
  while (!File(p.join(root, "config.dist")).existsSync()) {
    root = p.dirname(root);
  }

  // --------------
  // Create (or update) the conda environment
  // --------------

  print("--------------------------------------");
  print("Creating or updating conda environment");
  print("--------------------------------------");
  print("");

  final conda = Platform.environment["CONDA_EXE"];

  var sdconda = "";
  var base_args = <String>[];
 
  Process? condaProcess;

  if (conda != null && File(conda).existsSync()) {
    final env = p.join(root, 'condaenv');
    sdconda = conda;

    print("Using system Conda at $sdconda");

    base_args = ["-p", env];

    final testResult = Process.runSync(sdconda, ["run", ...base_args, "echo"]);

    if (testResult.exitCode == 0) {
      print("Environment exists. Updating.");
      condaProcess = await Process.start(sdconda, ["env", "update", ...base_args, "-f", "environment.yaml"]);
    }
    else {
      print("Environment doesn't exist. Creating.");
      condaProcess = await Process.start(sdconda, ["env", "create", ...base_args, "-f", "environment.yaml"]);
    }
  }
  else {
    final env = p.join(root, 'env');
    final micromamba = Platform.isLinux ? "micromamba-Linux" : "micromamba.exe" ;
    sdconda = p.join(env, micromamba);

    if (!File(sdconda).existsSync()) {
      Directory(env).createSync();
      File(p.join(root, "bin", micromamba)).copySync(sdconda);
    }

    print("Using local micromamba");

    base_args = ["-r", env, "-n", "gyre"];

    final testResult = Process.runSync(sdconda, ["list", ...base_args]);

    if (testResult.exitCode == 0) {
      print("Environment exists. Updating.");
      condaProcess = await Process.start(sdconda, ["update", ...base_args, "-y", "-f", "environment.yaml"]);
    }
    else {
      print("Environment doesn't exist. Creating.");
      condaProcess = await Process.start(sdconda, ["create", ...base_args, "-y", "-f", "environment.yaml"]);
    }
  }

  stdout.addStream(condaProcess.stdout);
  stderr.addStream(condaProcess.stderr);

  final condaResult = await condaProcess.exitCode;
  if (condaResult != 0) exit(condaResult);

  // --------------
  // Run the python script now we have an environment
  // --------------

  print("");
  print("--------------------------------------");
  print("Run main install script");
  print("--------------------------------------");
  print("");

  final Process pyProcess = await Process.start(sdconda, ["run", ...base_args, "python", p.join(root, "scripts", "install_or_update.py")]);

  stdout.addStream(pyProcess.stdout);
  stderr.addStream(pyProcess.stderr);

  final pyResult = await pyProcess.exitCode;
  if (pyResult != 0) exit(pyResult);

  // --------------
  // Create the run command linking into the used conda
  // --------------

  if (Platform.isLinux) {
    File(p.join(root, "run.sh")).writeAsStringSync("""
#!/bin/bash
${sdconda} run ${base_args.join(" ")} python ${p.join(root, 'scripts', 'run.py')}
""");
  }
  else {
    File(p.join(root, "run.cmd")).writeAsStringSync("""
@echo off
${sdconda} run ${base_args.join(" ")} python ${p.join(root, 'scripts', 'run.py')} || pause
""");
  }

  print("Done");
}


