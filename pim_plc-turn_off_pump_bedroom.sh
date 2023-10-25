#!/usr/bin/env bash

# working variables
#DATEVAR=date +%Y%m%d_%H%M
CURRENT_DATE=$(date +%Y%m%d_%H%M%S)
VERSION_VAR='(v1.0)'
LOG_FILE='/home/pi/Projects/pi-millenium/pi-millenium.log'
#CMD_FILE='/home/pi/Projects/pi-millenium/command2.csv'
CMD_FILE='/home/pi/Projects/pi-millenium/command.csv'

echo $CURRENT_DATE $VERSION_VAR $0 >> $LOG_FILE
echo 'r,nod,12,1' >> $CMD_FILE
