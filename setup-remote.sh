#!/bin/bash

INSTALL_PATH="$HOME/.local/bin"
PROGRAM_NAME="igem-cdn"
PROGRAM_DIR="$INSTALL_PATH/igem"

ensure_install_path() {
    if [ ! -d "$INSTALL_PATH" ]; then
        echo "$INSTALL_PATH does not exist. Creating it now."
        mkdir -p "$INSTALL_PATH"
        echo "$INSTALL_PATH created."
    fi
}

ensure_path() {
    if [[ ":$PATH:" != *":$INSTALL_PATH:"* ]]; then
        echo "Adding $INSTALL_PATH to PATH in .bashrc"
        echo -e "\n# Added by iGEM CDN Tool setup script on $(date)" >> "$HOME/.bashrc"
        echo "export PATH=\"$PATH:$INSTALL_PATH\"" >> "$HOME/.bashrc"
        echo "Please restart your terminal or run 'source ~/.bashrc' to update your PATH."
    fi
}

install_program() {
    ensure_install_path
    rm -rf "$INSTALL_PATH/$PROGRAM_NAME"
    rm -rf "$PROGRAM_DIR"
    mv "$PROGRAM_NAME" "$INSTALL_PATH/$PROGRAM_NAME"
    mkdir "$PROGRAM_DIR"
    mv igem-cdn-config.json "$PROGRAM_DIR/config.json"
    chmod +x "$INSTALL_PATH/$PROGRAM_NAME"
    ensure_path
    echo "iGEM CDN Tool installed successfully!"
    echo "Please restart your terminal."
}

uninstall_program() {
    rm -rf "$INSTALL_PATH/$PROGRAM_NAME"
    rm -rf "$PROGRAM_DIR"
    echo "iGEM CDN Tool uninstalled successfully!"
}

get_program() {
    ISA=$1
    if [ "$ISA" == "ARM" ]; then
        DOWNLOAD_URL="https://gitlab.igem.org/zivmax/igem-cdn/-/jobs/933640/artifacts/download?file_type=archive"
    elif [ "$ISA" == "X86" ]; then
        DOWNLOAD_URL="https://github.com/zivmax/igem-cdn/releases/download/v1.0.0/release.zip"
    else
        echo "Invalid ISA specified. Please choose 'ARM' or 'X86'."
        exit 1
    fi

    curl -L "$DOWNLOAD_URL" -o "igem-cdn-tool.zip"
    unzip igem-cdn-tool.zip
    rm igem-cdn-tool.zip
}

if [ "$1" == "uninstall" ]; then
    uninstall_program
elif [ "$1" == "install" ]; then
    if [ -z "$2" ]; then
        echo "Please specify the ISA: 'ARM' or 'X86'."
        exit 1
    fi
    get_program "$2"
    install_program
else
    echo "Please specify the action you want to perform: 'install' or 'uninstall'."
    echo "For installation, also specify the ISA: 'ARM' or 'X86'."
    exit 1
fi
