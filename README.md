# Gyre installer and idea2.art AIO

This is an easy installer for the [Gyre AI art server](https://gyre.ai)

There are also bundles available that include the idea2.art websystem, a user-friendly interface for AI art generation

# Usage

## Windows

### Without installing conda (note: does not work for Windows versions with non-roman alphabets, e.g. chinese, ukranian, etc)

- Download the latest "Source code (zip)" package from https://github.com/stablecabal/gyre-installer/releases/ (under "Assets")
  - The bundles labelled "idea2art" include idea2.art.
- Unpack the zip somewhere
- Run `install_or_update.exe` at least once (first to install, and then whenever you want to update to the latest version)
- Run `run.cmd` to start

### With conda

- If you don't already have an install of conda, install the latest version of miniconda from https://docs.conda.io/en/latest/miniconda.html 
- Download the latest "Source code (zip)" package from https://github.com/stablecabal/gyre-installer/releases/ (under "Assets")
- Unpack the zip somewhere
- Start an "Anaconda Prompt" from the start menu
  - Within the prompt, run `install_or_update.exe` at least once (first to install, and then whenever you want to update to the latest version)
  - Within the prompt, run `run.cmd` to start

## Linux

Same as Windows, but .sh instead of .cmd

## MacOS

Unfortunately not currently supported.

# License

Gyre and the cde specific to this installer is licensed under the Apache-2.0 license
Idea2.art and any bundle that includes it is licensed under the Affero GPL 3.0 - https://www.gnu.org/licenses/agpl-3.0.en.html
