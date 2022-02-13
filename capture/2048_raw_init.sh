#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "please run as root, 'sudo 2048_raw.sh'"
  exit
fi

# running axiom_start.sh twice will crash the camera, this should prevent that from happening
FILE=/tmp/axiom.started
if [[ -f "$FILE" ]]; then
    echo "AXIOM service seems to be running already, if that is not the case please remove the /tmp/axiom.started file and try again."
    exit
fi

memtool -1 -F 0x0 0x18000000 0x8000000
axiom_start.sh raw
axiom_gen_init_hdmi.sh 2048x1080p50
axiom_data_init_hdmi.sh
axiom_rmem_conf.sh 0
axiom_scn_reg 30 0x7000
axiom_raw_mark.sh
axiom_scn_reg 2 0x100
axiom_snap -b -2 -E -z

# running axiom_start.sh twice will crash the camera, this should prevent that from happening
touch /tmp/axiom.started
