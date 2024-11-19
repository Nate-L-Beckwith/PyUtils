#!/usr/bin/env python3

import os
import sys
import shutil
import requests
import gnupg
import apt
from pathlib import Path

def check_root():
    """Ensure the script is run as root."""
    if os.geteuid() != 0:
        print("This script must be run as root. Please use sudo or switch to the root user.")
        sys.exit(1)

def update_and_upgrade(cache):
    """Update package lists and upgrade existing packages."""
    print("Updating package lists...")
    cache.update()
    cache.open(None)
    cache.upgrade()
    cache.commit()
    cache.upgrade()

def install_packages(cache, package_names):
    """Install specified packages using apt."""
    print(f"Installing packages: {' '.join(package_names)}")
    if pkg_to_install:
        for pkg in pkg_to_install:
            pkg.mark_install()
        try:
            cache.commit()
        except Exception as e:
            print(f"Error installing packages: {e}")
            sys.exit(1)
            sys.exit(1)
    else:
        print("No packages to install.")

def download_gpg_key(url, output_path):
    """Download the GPG key from the specified URL."""
    print(f"Downloading GPG key from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"GPG key downloaded to {output_path}")
    except requests.RequestException as e:
        print(f"Failed to download GPG key: {e}")
        sys.exit(1)

def dearmor_gpg_key(gpg, input_path, output_path):
    """Convert ASCII GPG key to binary format."""
    print(f"De-armor GPG key from {input_path} to {output_path}...")
    key_data = f.read()
    try:
        import_result = gpg.import_keys(key_data)
        if not import_result:
            print("Failed to import GPG key.")
            sys.exit(1)
        with open(output_path, 'wb') as f_out:
            f_out.write(import_result.fingerprints[0].encode())
        print(f"GPG key imported and saved to: {output_path}")
        print(f"De-armor completed: {output_path}")
    except Exception as e:
        print(f"Error during de-arming GPG key: {e}")
        sys.exit(1)

def install_gpg_key(source, destination):
    """Move the GPG key to the trusted keyrings directory with appropriate permissions."""
    shutil.copy2(source, destination)
    try:
        shutil.move(source, destination)
        os.chmod(destination, 0o644)
        print("GPG key installed successfully.")
    except Exception as e:
        print(f"Failed to install GPG key: {e}")
        sys.exit(1)

def add_vscode_repository(repo_entry, repo_file):
    """Add the VS Code repository to the APT sources list."""
    print(f"Adding VS Code repository to {repo_file}...")
    try:
        with open(repo_file, 'w') as f:
            f.write(repo_entry + '\n')
        print("VS Code repository added successfully.")
    except Exception as e:
        print(f"Failed to add VS Code repository: {e}")
        sys.exit(1)

def install_vscode(cache):
    """Install Visual Studio Code using apt."""
    print("Installing Visual Studio Code...")
    pkg_to_install = []
    if 'code' in cache:
        pkg_to_install.append(cache['code'])
    else:
        print("Package 'code' not found in cache.")
        sys.exit(1)
    for pkg in pkg_to_install:
        pkg.mark_install()
    try:
        cache.commit()
        print("Visual Studio Code installed successfully.")
    except Exception as e:
        print(f"Failed to install Visual Studio Code: {e}")
        sys.exit(1)

def autoremove_packages(cache):
    """Remove unnecessary packages."""
    print("Removing unnecessary packages...")
    try:
        cache.autoremove()
        cache.commit()
        print("Unnecessary packages removed.")
    except Exception as e:
        print(f"Failed to remove unnecessary packages: {e}")
        sys.exit(1)

# Initialize GnuPG
gpg = gnupg.GPG()

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

    # GnuPG is already initialized globally

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
    # Update package lists to include the new VS Code repository
    print("Updating package lists to include the VS Code repository...")
    cache.update()
    cache.open(None)
    print("Updating package lists to include the VS Code repository...")
    cache.update()

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
        print(f"Removed temporary file {temp_gpg_dearmor}")

    print("Visual Studio Code has been installed successfully!")

if __name__ == "__main__":
    main()
