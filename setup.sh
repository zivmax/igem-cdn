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
    rm -rf $INSTALL_PATH/$PROGRAM_NAME
    rm -rf $PROGRAM_DIR
    cp ./dist/$PROGRAM_NAME $INSTALL_PATH/$PROGRAM_NAME
    mkdir $PROGRAM_DIR
    cp config.json $PROGRAM_DIR/config.json
    chmod +x $INSTALL_PATH/$PROGRAM_NAME
    ensure_path
    echo "iGEM CDN Tool installed successfully!"
    echo "Please restart your terminal."
}

uninstall_program() {
    rm -rf $INSTALL_PATH/$PROGRAM_NAME
    rm -rf $PROGRAM_DIR
    echo "iGEM CDN Tool uninstalled successfully!"
}

build_program() {
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        echo "Virtual environment not found, using system packages."
    fi
    
    python -m PyInstaller main.py --name $PROGRAM_NAME --hidden-import=_cffi_backend -F --clean --strip
}

if [ "$1" == "uninstall" ]; then
    uninstall_program
elif [ "$1" == "install" ]; then
    build_program
    install_program
elif [ "$1" == "build" ]; then
    build_program
else
    echo "Please specify the action you want to perform: 'install' or 'uninstall'."
fi
