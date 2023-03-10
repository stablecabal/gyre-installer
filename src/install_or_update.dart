import 'package:path/path.dart' as p;
import 'dart:io';

void main() async {
  final script = Platform.script.toFilePath();

  var root = p.dirname(script);
  while (!File(p.join(root, "config.dist")).existsSync()) {
    root = p.dirname(root);
  }

  final conda = Platform.environment["CONDA_EXE"];

  var sdconda = "";
  var base_args = <String>[];
  ProcessResult? couResult;

  if (conda != null && File(conda).existsSync()) {
    final env = p.join(root, 'condaenv');
    sdconda = conda;

    print("Using system Conda at $sdconda");

    base_args = ["-p", env];

    final testResult = Process.runSync(sdconda, ["run", ...base_args, "echo"]);

    if (testResult.exitCode == 0) {
      print("Environment exists. Updating.");
      couResult = Process.runSync(sdconda, ["env", "update", ...base_args, "-f", "environment.yaml"]);
    }
    else {
      print("Environment doesn't exist. Creating.");
      couResult = Process.runSync(sdconda, ["env", "create", ...base_args, "-f", "environment.yaml"]);
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
      couResult = Process.runSync(sdconda, ["update", ...base_args, "-y", "-f", "environment.yaml"]);
    }
    else {
      print("Environment doesn't exist. Creating.");
      couResult = Process.runSync(sdconda, ["create", ...base_args, "-y", "-f", "environment.yaml"]);
    }
  }

  if (couResult.exitCode != 0) {
    print("Error. Could not create or update python environment. Message from Conda:");
    print(couResult.stderr);
    throw new Error();
  }
  else {
    print(couResult.stdout);
  }

  final Process process = await Process.start(sdconda, ["run", ...base_args, "python", p.join(root, "scripts", "install_or_update.py")]);
  process.stdout.pipe(stdout);
  process.stderr.pipe(stderr);

  final result = await process.exitCode;
  
  if (Platform.isLinux) {
    File(p.join(root, "run.sh")).writeAsStringSync("""
#!/bin/bash
${sdconda} run ${base_args.join(" ")} python ${p.join(root, 'scripts', 'run.py')}
""");
  }
  else {
    File(p.join(root, "run.cmd")).writeAsStringSync("""
@echo off
start ${sdconda} run ${base_args.join(" ")} python ${p.join(root, 'scripts', 'run.py')}
""");
  }


  print("Done");
}


