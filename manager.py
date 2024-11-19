# vscd_manager/manager.py

import os
import sys
import shutil
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List

import requests
import apt
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from .utils import run_command

# -------------------------------
# Configuration and Constants
# -------------------------------

# VS Code Configuration Paths
CONFIG_PATHS = [
    Path("~/.config/Code").expanduser(),
    Path("~/.vscode").expanduser(),
    Path("~/.cache/Code").expanduser(),
    Path("~/.local/share/code").expanduser(),
    Path("~/.config/Code/Crashpad").expanduser(),
]

# VS Code Download URL
VSCODE_DEB_URL = "https://update.code.visualstudio.com/latest/linux-deb-x64/stable"

# Temporary DEB file name
TEMP_DEB_NAME = "vscode_latest.deb"

# -------------------------------
# VSCManager Class
# -------------------------------

logger = logging.getLogger(__name__)

class VSCManager:
    def __init__(self, deb_url: str = VSCODE_DEB_URL):
        self.deb_url = deb_url
        self.temp_deb_path = Path(tempfile.gettempdir()) / TEMP_DEB_NAME

    def check_root(self):
        """Ensure the script is run with root privileges."""
        if os.geteuid() != 0:
            logger.error("This script must be run as root. Use sudo.")
            sys.exit(1)

    def uninstall_vscode(self):
        """Uninstall VS Code and remove old config files."""
        cache = apt.Cache()
        if "code" in cache and cache["code"].is_installed:
            logger.info("Uninstalling VS Code .deb package")
            run_command(["apt", "purge", "-y", "code"])
            self.remove_config()
        else:
            logger.info("VS Code is not installed as a .deb package")

    def remove_config(self):
        """Remove residual configuration and data files for VS Code."""
        logger.info("Removing configuration and data files for VS Code")
        for path in CONFIG_PATHS:
            if path.exists():
                try:
                    shutil.rmtree(path)
                    logger.debug(f"Removed {path}")
                except Exception as e:
                    logger.warning(f"Failed to remove {path}: {e}")

    def install_dependencies(self):
        """Update system package list and install required dependencies for VS Code."""
        logger.info("Updating system package list and installing dependencies")
        run_command(["apt", "update"])
        dependencies = [
            "libgtk-3-0", "libxss1", "libasound2", "libnss3", "libx11-xcb1",
            "libxcb1", "libxcomposite1", "libxcursor1", "libxdamage1",
            "libxi6", "libxtst6"
        ]
        run_command(["apt", "install", "-y"] + dependencies)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(5),
        retry=retry_if_exception_type(RequestException),
        reraise=True
    )
    def download_vscode(self):
        """Download the latest VS Code .deb package with retry mechanism."""
        logger.info("Downloading the latest VS Code .deb package")
        response = requests.get(self.deb_url, stream=True, timeout=10)
        response.raise_for_status()
        with self.temp_deb_path.open("wb") as file:
            shutil.copyfileobj(response.raw, file)
        logger.info(f"Download complete: {self.temp_deb_path}")

    def install_vscode(self):
        """Install the downloaded VS Code .deb package."""
        logger.info(f"Installing VS Code from {self.temp_deb_path}")
        try:
            run_command(["dpkg", "-i", str(self.temp_deb_path)])
        except subprocess.CalledProcessError:
            logger.info("Resolving dependencies")
            run_command(["apt", "install", "-f", "-y"])

    def verify_installation(self):
        """Verify that VS Code has been installed correctly."""
        try:
            run_command(
                ["code", "--version"],
                check=True,
                capture_output=True
            )
            logger.info("VS Code installed successfully")
        except subprocess.CalledProcessError:
            logger.error("VS Code installation failed")
            sys.exit(1)

    def handle_install(self):
        """Handle the installation process."""
        self.install_dependencies()
        self.download_vscode()
        self.install_vscode()
        self.verify_installation()

    def handle_update(self):
        """Handle the update process."""
        cache = apt.Cache()
        if "code" in cache and cache["code"].is_installed:
            logger.info("Updating VS Code")
            self.handle_install()
        else:
            logger.info("VS Code is not installed. Proceeding with installation.")
            self.handle_install()

    def handle_refresh(self):
        """Handle the refresh process: uninstall and reinstall."""
        self.uninstall_vscode()
        self.handle_install()

    def handle_default_action(self):
        """Default behavior: update if installed, otherwise install."""
        self.handle_update()

    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_deb_path.exists():
            try:
                self.temp_deb_path.unlink()
                logger.debug(f"Removed temporary file: {self.temp_deb_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {e}")
