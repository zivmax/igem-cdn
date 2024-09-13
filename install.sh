rm -rf $HOME/.local/bin/igem-upload
rm -rf $HOME/.local/bin/igem
cp main.py $HOME/.local/bin/igem-upload
mkdir $HOME/.local/bin/igem
cp config.json $HOME/.local/bin/igem/config.json
cp src/uploads.py $HOME/.local/bin/igem/uploads.py
chmod +x $HOME/.local/bin/igem-upload
echo "iGEM Upload installed successfully!"
echo "Please restart your terminal."
