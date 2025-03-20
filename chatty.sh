#!/usr/bin/env bash
source bin/activate

if [ -f "chatty.env" ]; then  source "chatty.env"; fi
python bot.py
