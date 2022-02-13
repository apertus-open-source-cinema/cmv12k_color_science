#!/bin/bash

#create directory
mkdir 1xgain_$3x_$2
cd 1xgain_$3x_$2
echo "created directory: 1xgain_$3x_$2"


# capture one raw snap before the averaging sequence to log the image sensor temperature before 
echo "capturing 1 raw snaps"
ssh root@$1 "axiom_snap -2 -b -r -e $2" > snap01_$2.raw12


#capture sequence
echo "capturing raw sequence average"
for time in 1; do cargo run --release -- WebcamInput --device 0 ! DualFrameRawDecoder --first-red-x true --first-red-y false ! Average --n=$3 ! RawBlobWriter --number-of-frames $3 --path target/frame_1x_$(ssh operator@$1 "echo $time > /axiom-api/devices/cmv12000/computed/exposure_time_ms/value; cat /axiom-api/devices/cmv12000/computed/exposure_time_ms/value").blob; done


#capture snaps
echo "capturing 3 more raw snaps"
ssh root@$1 "axiom_snap -2 -b -r -e $2" > snap02_$2.raw12
ssh root@$1 "axiom_snap -2 -b -r -e $2" > snap03_$2.raw12
ssh root@$1 "axiom_snap -2 -b -r -e $2" > snap04_$2.raw12
