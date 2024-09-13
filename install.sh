rm -rf $HOME/.local/bin/igem-upload
rm -rf $HOME/.local/bin/igem
pyinstaller --name igem-upload --onefile main.py
cp ./dist/igem-upload $HOME/.local/bin/igem-upload
mkdir $HOME/.local/bin/igem
cp config.json $HOME/.local/bin/igem/config.json
chmod +x $HOME/.local/bin/igem-upload
echo "iGEM Upload installed successfully!"
echo "Please restart your terminal."
