#!/usr/bin/env bash
source coffy-env/bin/activate

if [ -f "chatty.env" ]; then  source "chatty.env"; fi
python chatty.db.py
