#!/bin/bash

ANACONDA_VERSION="2024.10-1"
ANACONDA_INSTALL_DIR="$HOME/anaconda3"
ANACONDA_INSTALLER="Anaconda3-${ANACONDA_VERSION}-Linux-x86_64.sh"
ANACONDA_URL="https://repo.anaconda.com/archive/${ANACONDA_INSTALLER}"

# Function to print messages
function echo_message {
    echo -e "\n====================\n$1\n====================\n"
}

# Check if Anaconda is already installed
if [ -d "$ANACONDA_INSTALL_DIR" ]; then
    echo_message "Anaconda is already installed in $ANACONDA_INSTALL_DIR."
    exit 0
fi

# Download Anaconda installer
echo_message "Downloading Anaconda installer..."
wget -O "$ANACONDA_INSTALLER" "$ANACONDA_URL"

# Verify the installer exists
if [ ! -f "$ANACONDA_INSTALLER" ]; then
    echo_message "Failed to download Anaconda installer."
    exit 1
fi

# Run the Anaconda installer
echo_message "Running the Anaconda installer..."
bash "$ANACONDA_INSTALLER" -b -p "$ANACONDA_INSTALL_DIR"

# Add Anaconda to PATH
echo_message "Adding Anaconda to PATH..."
eval "$(${ANACONDA_INSTALL_DIR}/bin/conda shell.bash hook)"
echo "export PATH=\"$ANACONDA_INSTALL_DIR/bin:\$PATH\"" >> ~/.bashrc

# Initialize Conda
echo_message "Initializing Conda..."
source ~/.bashrc
conda init

# Clean up the installer
echo_message "Cleaning up the Anaconda installer..."
rm -f "$ANACONDA_INSTALLER"

echo_message "Creating a default Conda environment"
conda create -n default_env python -y 
conda activate default_env
# Verify Anaconda installation
if command -v conda &> /dev/null; then
    echo_message "Anaconda installation and configuration is complete."

    # Ensure the base environment is enabled and activated
    echo_message "Activating the base Conda environment..."
    conda activate base
else
    echo_message "Anaconda installation failed. Please check the logs for details."
    exit 1
fi
