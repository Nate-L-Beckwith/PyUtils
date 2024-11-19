# utils.py

import os
import sys
import shutil
import requests
import gnupg


def check_root():
    """ensure the script is run as root."""
    if os.geteuid() != 0:
        print("this script must be run as root. please use sudo or switch to the root user.")
        sys.exit(1)

def update_and_upgrade(cache):
    """update package lists and upgrade existing packages."""
    print("updating package lists...")
    cache.update()
    cache.open(None)
    cache.upgrade()
    cache.commit()
    cache.upgrade()

def install_packages(cache, package_names):
    """install specified packages using apt."""
    print(f"installing packages: {' '.join(package_names)}")
    pkg_to_install = [cache[pkg] for pkg in package_names if pkg in cache]
    if pkg_to_install:
        for pkg in pkg_to_install:
            pkg.mark_install()
        try:
            cache.commit()
        except Exception as e:
            print(f"error installing packages: {e}")
            sys.exit(1)
    else:
        print("no packages to install.")

def download_gpg_key(url, output_path):
    """download the gpg key from the specified url."""
    print(f"downloading gpg key from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"gpg key downloaded to {output_path}")
    except requests.RequestException as e:
        print(f"failed to download gpg key: {e}")
        sys.exit(1)

def dearmor_gpg_key(gpg, input_path, output_path):
    """convert ascii gpg key to binary format."""
    print(f"de-armor gpg key from {input_path} to {output_path}...")
    try:
        with open(input_path, 'r') as f:
            key_data = f.read()
        import_result = gpg.import_keys(key_data)
        if not import_result:
            print("failed to import gpg key.")
            sys.exit(1)
        with open(output_path, 'wb') as f_out:
            f_out.write(import_result.fingerprints[0].encode())
        print(f"gpg key imported and saved to: {output_path}")
    except Exception as e:
        print(f"error during de-arming gpg key: {e}")
        sys.exit(1)

def install_gpg_key(source, destination):
    """move the gpg key to the trusted keyrings directory with appropriate permissions."""
    try:
        shutil.move(source, destination)
        os.chmod(destination, 0o644)
        print("gpg key installed successfully.")
    except Exception as e:
        print(f"failed to install gpg key: {e}")
        sys.exit(1)

def add_vscode_repository(repo_entry, repo_file):
    """add the vs code repository to the apt sources list."""
    print(f"adding vs code repository to {repo_file}...")
    try:
        with open(repo_file, 'w') as f:
            f.write(repo_entry + '\n')
        print("vs code repository added successfully.")
    except Exception as e:
        print(f"failed to add vs code repository: {e}")
        sys.exit(1)

def install_vscode(cache):
    """install visual studio code using apt."""
    print("installing visual studio code...")
    if 'code' in cache:
        pkg = cache['code']
        pkg.mark_install()
        try:
            cache.commit()
            print("visual studio code installed successfully.")
        except Exception as e:
            print(f"failed to install visual studio code: {e}")
            sys.exit(1)
    else:
        print("package 'code' not found in cache.")
        sys.exit(1)

def autoremove_packages(cache):
    """remove unnecessary packages."""
    print("removing unnecessary packages...")
    try:
        cache.autoremove()
        cache.commit()
        print("unnecessary packages removed.")
    except Exception as e:
        print(f"failed to remove unnecessary packages: {e}")
        sys.exit(1)
