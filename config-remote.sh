#!/bin/bash

FILE_URL="https://raw.githubusercontent.com/zivmax/igem-cdn/refs/heads/main/igem-cdn-config.json"
FILE_NAME="igem-cdn-config.json"

echo "Downloading Config template..."
curl -L "$FILE_URL" -o "$FILE_NAME"

code "$FILE_NAME"
