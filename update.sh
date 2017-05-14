#! /bin/bash

UPDATE_CMD=/home/lskital/src/home_automation/env_update.py
DST_DIR='/var/www/html'
SRC_DIR='/home/lskital/src/rrd/gen'

if $UPDATE_CMD; then
  cp $SRC_DIR/* $DST_DIR
fi
