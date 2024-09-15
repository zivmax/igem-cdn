#!/bin/bash

INSTALL_PATH="$HOME/.local/bin"
PROGRAM_NAME="igem-upload"
PROGRAM_DIR="$INSTALL_PATH/igem"

install_program() {
    rm -rf build/ dist/ igem_upload.spec
    pyinstaller --name $PROGRAM_NAME --onefile main.py
    rm -rf $INSTALL_PATH/$PROGRAM_NAME
    rm -rf $PROGRAM_DIR
    cp ./dist/$PROGRAM_NAME $INSTALL_PATH/$PROGRAM_NAME
    mkdir $PROGRAM_DIR
    cp config.json $PROGRAM_DIR/config.json
    chmod +x $INSTALL_PATH/$PROGRAM_NAME
    echo "iGEM Upload installed successfully!"
    echo "Please restart your terminal."
}

uninstall_program() {
    rm -rf $INSTALL_PATH/$PROGRAM_NAME
    rm -rf $PROGRAM_DIR
    echo "iGEM Upload uninstalled successfully!"
}

if [ "\$1" == "uninstall" ]; then
    uninstall_program
elif [ "\$1" == "install" ]; then
    install_program
else
    echo "Please specify the action you want to perform: 'install' or 'uninstall'."
fi
