# IDEA2.ART all-in-one

This is a combined client and server for IDEA2.ART, a user-friendly interface to the AI art generation system Stable Diffusion

# Usage

## Windows

### Without installing conda (note: does not work for Windows versions with non-roman alphabets, e.g. chinese, ukranian, etc)

- Download the latest "Source code (zip)" package from https://github.com/hafriedlander/idea2art-aio/releases/ (under "Assets")
- Unpack the zip somewhere
- Run install_or_update.cmd at least once (first to install, and then whenever you want to update to the latest version)
- Edit the config file that is created and set the first value to contain your Huggingface token
  - If you don't have a huggingface token yet
    - Register for a HuggingFace account at https://huggingface.co/join
    - Follow the instructions to access the repository at https://huggingface.co/CompVis/stable-diffusion-v1-4
    - Create a token at https://huggingface.co/settings/tokens
- Run run.cmd to start

Visit http://127.0.0.1:5000/ in your browser

### With conda

- If you don't already have an install of conda, install the latest version of miniconda from https://docs.conda.io/en/latest/miniconda.html 
- Follow the instructions from the "Without installing conda" section

## Linux / MacOS

Not tested. Possibly, same as for Windows but with .sh instead of .cmd

# License

Affero GPL 3.0 - https://www.gnu.org/licenses/agpl-3.0.en.html

The server component is available seperately, and that is distributable under Apache 2.0