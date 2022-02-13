#!/bin/bash

#create directory
mkdir $(date +"%Y-%m-%d_%H_%I")_1xgain_$3x_$2
cd $(date +"%Y-%m-%d_%H_%I")_1xgain_$3x_$2
echo "created directoy: $(date +"%Y-%m-%d_%H_%I")_1xgain_$3x_$2"


#set exposure time
ssh root@$1 "axiom_snap -2 -b -r -e $2 -z"


# capture one raw snap before the averaging sequence to log the image sensor temperature before 
echo "capturing 1 raw snap"
ssh root@$1 "axiom_sequencer_stop.sh"
ssh root@$1 "axiom_snap -2 -b -r -e $2" > snap01_$2.raw12
ssh root@$1 "axiom_sequencer_start.sh"



#capture sequence
echo "capturing raw sequence average"
for time in 1; do cargo run --release -- WebcamInput --device 0 ! DualFrameRawDecoder ! Average --n=$3 ! RawBlobWriter --number-of-frames=1 --path frame_averaged_$(ssh root@$1 "cat /axiom-api/devices/cmv12000/computed/exposure_time_ms/value").blob; done


#capture snaps
echo "capturing 3 more raw snaps"
ssh root@$1 "axiom_sequencer_stop.sh"
ssh root@$1 "axiom_snap -2 -b -r -e $2" > snap02_$2.raw12
ssh root@$1 "axiom_snap -2 -b -r -e $2" > snap03_$2.raw12
ssh root@$1 "axiom_snap -2 -b -r -e $2" > snap04_$2.raw12
ssh root@$1 "axiom_sequencer_start.sh"

cd ..

tar --use-compress-program zstd -cf $(date +"%Y-%m-%d_%H_%I")_1xgain_$3x_$2.tar.zst $(date +"%Y-%m-%d_%H_%I")_1xgain_$3x_$2/
echo "compressed $(date +"%Y-%m-%d_%H_%I")_1xgain_$3x_$2.tar.zst"