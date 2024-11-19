# wapp
wrap python scripts in a module

## Description
This tool simplifies working with remote Python Git repositories by transforming them into flexible, reusable packages. Previously, using such repositories required manual installation of dependencies using pip, which could conflict with other project requirements. In addition, when using virtual environments, the user had to set up and navigate to the directory containing the scripts each time in order to activate and re-use them - extra steps which can be avoided

Key Features:
  * pipx Compatibility: Install repositories as standalone packages in isolated virtual environments via pipx, ensuring clean, independent installations.
  * Module Reusability: Seamlessly import code from the wrapped repository as a module into your own Python projects.

Additional functionality includes:
  * Custom Function Names: Define custom names for exposed functions to avoid conflicts with other packages.
  * Dependency Management: Add extra dependencies or modify entries in the repository's requirements.txt.
  * Repository Updates: Easily update wrapped repositories to stay in sync with the latest changes.


## Installation
```
pipx install git+https://github.com/osown/wapp
```
## Usage
```
wapp -h
usage: wapp.py [-h] {create,update} ...

wrap as python package

positional arguments:
  {create,update}
    create         create crafted python package
    update         update crafted python package

options:
  -h, --help       show this help message and exit
```

Example 1: Add additional dependencies, autodetect scripts and install via pipx after successful build
```
wapp create --pipx --requires impacket ldap3 dnspython -- https://github.com/dirkjanm/krbrelayx
```

Example 2: Specify an alternate name for an existing script and install via pipx after successful build
```
wapp create --pipx --scripts dump.py:frida-ios-dump.py -- https://github.com/AloneMonkey/frida-ios-dump
```

Example 3: Update existing wrapped repo and upgrade via pipx
```
wapp update --pipx frida_ios_dump
```

## Output
```
wapp create --pipx --requires impacket ldap3 dnspython -- https://github.com/dirkjanm/krbrelayx

Created /opt/tools/win/ad/krbrelayx
Cloning https://github.com/dirkjanm/krbrelayx into /opt/tools/win/ad/krbrelayx/krbrelayx
Enumerating exposed scripts:
Exposed scripts:
  printerbug.py -> printerbug.py
  addspn.py -> addspn.py
  dnstool.py -> dnstool.py
  krbrelayx.py -> krbrelayx.py
Successfully created wrapped package krbrelayx
Package revision: 0.0.0.dev0+20241110.225709.054d2a2
Running "pipx install /opt/tools/win/ad/krbrelayx":
  creating virtual environment...
  determining package name from '/opt/tools/win/ad/krbrelayx'...
  creating virtual environment...
  installing krbrelayx from spec '/opt/tools/win/ad/krbrelayx'...
  done! ✨ 🌟 ✨
    installed package krbrelayx 0.0.0.dev0+20241110.225709.054d2a2, installed using Python 3.12.7
    These apps are now globally available
      - addspn.py
      - dnstool.py
      - krbrelayx.py
      - printerbug.py
pipx exited with: 0
```