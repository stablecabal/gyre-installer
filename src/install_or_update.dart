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
  print("Creating or updating python environment");
  print("--------------------------------------");
  print("");

  final conda = Platform.environment["CONDA_EXE"];
  final has_system_conda = conda != null && File(conda).existsSync();

  final conda_env = p.join(root, 'condaenv');
  final umamba_env = p.join(root, 'env');

  bool? use_system_conda = null;

  print("$conda_env, $umamba_env");

  if (has_system_conda && Directory(conda_env).existsSync()) {
    use_system_conda = true;
  } else if (Directory(umamba_env).existsSync()) {
    use_system_conda = false;
  } else if (has_system_conda) {
    while (use_system_conda == null) {
      print("Which python environment manager would you like to use:");
      print(
          "  1: [Default] The built-in 'micromamba' python environment manager");
      print("  2: The system 'conda' python environment manager");
      print("Enter '1', '2', 'q' to abort, or press enter to use the default");

      final line = stdin.readLineSync();
      if (line != null) {
        if (line == "") {
          use_system_conda = false;
        } else if (line == "q") {
          print("Aborting");
          exit(-1);
        } else {
          final try_answer = int.tryParse(line);
          if (try_answer != null && try_answer >= 1 && try_answer <= 2) {
            use_system_conda = (try_answer == 2);
          }
        }
      }

      if (use_system_conda == null) {
        print("Please enter 1 or 2");
        print("");
      }
    }
  } else {
    use_system_conda = false;
  }

  var sdconda = "";
  var base_args = <String>[];
  var run_args = <String>[];

  Process? condaProcess;

  if (use_system_conda) {
    final env = conda_env;
    sdconda = conda!;

    print("Using system conda at $sdconda");

    base_args = ["-p", env];
    run_args = ["--no-capture-output"];

    final testResult = Process.runSync(sdconda, ["run", ...base_args, "echo"]);

    if (testResult.exitCode == 0) {
      print("Environment exists. Updating.");
      condaProcess = await Process.start(
          sdconda, ["env", "update", ...base_args, "-f", "environment.yaml"]);
    } else {
      print("Environment doesn't exist. Creating.");
      condaProcess = await Process.start(
          sdconda, ["env", "create", ...base_args, "-f", "environment.yaml"]);
    }
  } else {
    final env = p.join(root, 'env');
    final micromamba = Platform.isLinux ? "micromamba-Linux" : "micromamba.exe";
    sdconda = p.join(env, micromamba);

    if (!File(sdconda).existsSync()) {
      Directory(env).createSync();
      File(p.join(root, "bin", micromamba)).copySync(sdconda);
    }

    print("Using built-in micromamba");

    base_args = ["-r", env, "-n", "gyre"];

    final testResult = Process.runSync(sdconda, ["list", ...base_args]);

    if (testResult.exitCode == 0) {
      print("Environment exists. Updating.");
      condaProcess = await Process.start(
          sdconda, ["update", ...base_args, "-y", "-f", "environment.yaml"]);
    } else {
      print("Environment doesn't exist. Creating.");
      condaProcess = await Process.start(
          sdconda, ["create", ...base_args, "-y", "-f", "environment.yaml"]);
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

  final Process pyProcess = await Process.start(sdconda, [
    "run",
    ...run_args,
    ...base_args,
    "python",
    p.join(root, "scripts", "install_or_update.py")
  ]);

  pyProcess.stdin.addStream(stdin);
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
${sdconda} run ${run_args.join(" ")} ${base_args.join(" ")} python ${p.join(root, 'scripts', 'run.py')}
""");
  } else {
    File(p.join(root, "run.cmd")).writeAsStringSync("""
@echo off
${sdconda} run ${run_args.join(" ")} ${base_args.join(" ")} python ${p.join(root, 'scripts', 'run.py')} || pause
""");
  }

  print("Done");
}
