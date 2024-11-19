# apt_instl_vscode.py

import os
import sys
import shutil
import requests
import gnupg
import apt
from pathlib import Path
from utils import *

def main():
    check_root()

    # Initialize python-apt cache
    cache = apt.Cache()

    # Update and upgrade
    update_and_upgrade(cache)

    # Install required packages: wget and gpg
    install_packages(cache, ['wget', 'gpg'])

    # Download Microsoft's GPG key
    gpg_key_url = 'https://packages.microsoft.com/keys/microsoft.asc'
    temp_gpg_armor = '/tmp/microsoft.asc'
    temp_gpg_dearmor = '/tmp/microsoft.gpg'
    download_gpg_key(gpg_key_url, temp_gpg_armor)

    # Initialize GnuPG
    gpg = gnupg.GPG()

    # De-armor the GPG key
    dearmor_gpg_key(gpg, temp_gpg_armor, temp_gpg_dearmor)

    # Install the GPG key to /usr/share/keyrings/
    destination_keyring = '/usr/share/keyrings/microsoft.gpg'
    install_gpg_key(temp_gpg_dearmor, destination_keyring)

    # Remove the ASCII-armored key
    if os.path.exists(temp_gpg_armor):
        os.remove(temp_gpg_armor)
        print(f"Removed temporary file {temp_gpg_armor}")

    # Add the VS Code repository
    repo_entry = 'deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/vscode stable main'
    repo_file = '/etc/apt/sources.list.d/vscode.list'
    add_vscode_repository(repo_entry, repo_file)

    # Update package lists to include the new VS Code repository
    print("Updating package lists to include the VS Code repository...")
    cache.update()
    cache.open(None)

    # Install Visual Studio Code
    install_vscode(cache)

    # Clean up unnecessary packages
    autoremove_packages(cache)

    # Optionally, remove the temporary GPG file if it still exists and is not being used by another process
    if os.path.exists(temp_gpg_dearmor):
        try:
            os.remove(temp_gpg_dearmor)
            print(f"Removed temporary file {temp_gpg_dearmor}")
        except OSError as e:
            print(f"Error removing temporary file {temp_gpg_dearmor}: {e}")

    print("Visual Studio Code has been installed successfully!")

if __name__ == "__main__":
    main()
