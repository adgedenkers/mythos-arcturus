#!/usr/bin/env bash

ZIP_DIR="/opt/mythos/conversation_log_zips"
MYTHOS_DIR="/opt/mythos/conversations"
OBSIDIAN_DIR="/home/adge/curated-vault/spiritual/seraphe/tarot-sessions"

for zip in "$ZIP_DIR"/tarot*.zip; do
    name=$(basename "$zip" .zip)

    mkdir -p "$MYTHOS_DIR/$name"
    mkdir -p "$OBSIDIAN_DIR/$name"

    unzip -o "$zip" -d "$MYTHOS_DIR/$name"
    unzip -o "$zip" -d "$OBSIDIAN_DIR/$name"

done
