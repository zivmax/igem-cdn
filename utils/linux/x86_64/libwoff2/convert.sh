#!/bin/bash

# Specify the path to the woff2_compress binary if it's not in your PATH
WOFF2_COMPRESS_PATH="./cwoff2"

# Check if the woff2_compress binary exists
if [ ! -f "$WOFF2_COMPRESS_PATH" ]; then
    echo "cwoff2 not found at $WOFF2_COMPRESS_PATH"
    exit 1
fi

# Find all .ttf files in the current working directory
for ttf_file in *.ttf; do
    # Check if there are any .ttf files
    if [ "$ttf_file" == "*.ttf" ]; then
        echo "No .ttf files found in the current directory."
        exit 0
    fi

    # Convert .ttf to .woff2
    "$WOFF2_COMPRESS_PATH" "$ttf_file"
    
    # Check if conversion was successful
    if [ $? -eq 0 ]; then
        echo "Converted $ttf_file to ${ttf_file%.ttf}.woff2"
        # Delete the original .ttf file
        rm "$ttf_file"
        echo "Deleted $ttf_file"
    else
        echo "Failed to convert $ttf_file"
    fi
done
