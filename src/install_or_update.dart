import 'package:path/path.dart' as p;
import 'dart:io';

void main() async {
  final script = Platform.script.toFilePath();
  final root = p.dirname(script);
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
    sdconda = p.join(env, "micromamba.exe");

    if (!File(sdconda).existsSync()) {
      Directory(env).createSync();
      File(p.join(root, "micromamba", "micromamba.exe")).copySync(sdconda);
    }

    print("Using local micromamba");

    base_args = ["-r", env, "-n", "sd-grpc-server"];

    final testResult = Process.runSync(sdconda, ["run", ...base_args, "echo"]);

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
  
  File(p.join(root, "run.cmd")).writeAsStringSync("""
@echo off
start ${sdconda} run ${base_args.join(" ")} python ${p.join(root, 'scripts', 'run.py')}
  """);

  print("Done");
}


