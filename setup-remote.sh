#!/bin/bash

# Determine the install path based on the OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    INSTALL_PATH="/usr/local/bin"
    SHELL_CONFIG="$HOME/.zshrc"
else
    INSTALL_PATH="$HOME/.local/bin"
    SHELL_CONFIG="$HOME/.bashrc"
fi

PROGRAM_NAME="igem-cdn"
PROGRAM_DIR="$HOME/.local/share/igem"

ensure_install_path() {
    if [ ! -d "$INSTALL_PATH" ]; then
        echo "$INSTALL_PATH does not exist. Creating it now."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sudo mkdir -p "$INSTALL_PATH"
            echo "$INSTALL_PATH created."
        else
            mkdir -p "$INSTALL_PATH"
            echo "$INSTALL_PATH created."
        fi
    fi
}

ensure_path() {
    if [[ ":$PATH:" != *":$INSTALL_PATH:"* ]]; then
        echo "Adding $INSTALL_PATH to PATH in $SHELL_CONFIG"
        echo -e "\n# Added by iGEM CDN Tool setup script on $(date)" >> "$SHELL_CONFIG"
        echo "export PATH=\"$PATH:$INSTALL_PATH\"" >> "$SHELL_CONFIG"
        echo "Please restart your terminal or run 'source $SHELL_CONFIG' to update your PATH."
    fi
}

install_program() {
    ensure_install_path
    
    local is_update=false
    if [ -f "$INSTALL_PATH/$PROGRAM_NAME" ]; then
        is_update=true
    fi

    if [[ "$OSTYPE" == "darwin"* ]]; then
        sudo rm -rf "$INSTALL_PATH/$PROGRAM_NAME"
        sudo mv "$PROGRAM_NAME" "$INSTALL_PATH/$PROGRAM_NAME"
        sudo chmod +x "$INSTALL_PATH/$PROGRAM_NAME"
    else
        rm -rf "$INSTALL_PATH/$PROGRAM_NAME"
        mv "$PROGRAM_NAME" "$INSTALL_PATH/$PROGRAM_NAME"
        chmod +x "$INSTALL_PATH/$PROGRAM_NAME"
    fi

    if [[ ! -f "$PROGRAM_DIR/config.json" || -f "igem-cdn-config.json" ]]; then
        rm -rf "$PROGRAM_DIR"
        mkdir -p "$PROGRAM_DIR"
        mv igem-cdn-config.json "$PROGRAM_DIR/config.json"
    fi

    ensure_path

    echo "iGEM CDN Tool installed successfully!"
    if [ "$is_update" = false ]; then
        echo "Please restart your terminal."
    else
        echo "This is a update, no need to restart your terminal."
    fi
}

uninstall_program() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sudo rm -rf "$INSTALL_PATH/$PROGRAM_NAME"
    else
        rm -rf "$INSTALL_PATH/$PROGRAM_NAME"
    fi
    rm -rf "$PROGRAM_DIR"
    echo "iGEM CDN Tool uninstalled successfully!"
}

get_program() {
    ARCH=$(uname -m)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected MacOS"
        if [[ "$ARCH" == "arm64" ]]; then
            echo "Detected Apple Silicon"
            DOWNLOAD_URL="https://github.com/zivmax/igem-cdn/releases/download/latest/release-macos-latest-arm64.zip"
        elif [[ "$ARCH" == "x86_64" ]]; then
            echo "Detected Intel"
            DOWNLOAD_URL="https://github.com/zivmax/igem-cdn/releases/download/latest/release-macos-13-x86_64.zip"
        else
            echo "Unsupported architecture: $ARCH"
            exit 1
        fi
    else
        echo "Detected Linux"
        if [[ "$ARCH" == "aarch64" ]]; then
            echo "Detected ARM64"
            DOWNLOAD_URL="https://github.com/zivmax/igem-cdn/releases/download/latest/release-ubuntu-latest-arm64.zip"
        elif [[ "$ARCH" == "x86_64" ]]; then
            echo "Detected x86_64"
            DOWNLOAD_URL="https://github.com/zivmax/igem-cdn/releases/download/latest/release-ubuntu-latest-x86_64.zip"
        else
            echo "Unsupported architecture: $ARCH"
            exit 1
        fi
    fi

    curl -L "$DOWNLOAD_URL" -o "igem-cdn-tool.zip"
    unzip igem-cdn-tool.zip
    rm igem-cdn-tool.zip
}

if [ "$1" == "uninstall" ]; then
    uninstall_program
elif [ "$1" == "install" ]; then
    get_program
    install_program
else
    echo "Please specify the action you want to perform: 'install' or 'uninstall'."
    exit 1
fi
