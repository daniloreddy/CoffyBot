#!/usr/bin/env bash
cd /redberry/chatty.v2

source bin/activate

cd bot
if [ -f "chatty.env" ]; then  source "chatty.env"; fi
python chatty.db.py
