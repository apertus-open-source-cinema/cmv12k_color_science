# Prerequisites
* you need a recent Firmware 2.0 running on your AXIOM Beta.
* Your AXIOM Recorder device needs to have a keypair installed on the AXIOM Beta for passwordless root access to the Beta
* In the Magewell Setup Tool (usbcaptureutility) in the advanced HDMI settings -> Resolution set 2048x1080 as only resolution on the left column and 50 FPS as only framerate option, then save to device and reconnect device. 

# Usage
On the AXIOM Beta initialize the 4096 pixel wide raw mode with running the init script (as root) available from this repository instead of axiom_start.sh:
```
sudo su
2048_raw_init.sh
```


To capture and pack an averaged frame on the AXIOM Recorder run:

```
./capture_calibration_frame.sh *Beta-IP* *exposure-time* *number-of-frames*
```

example:

```
./capture_calibration_frame.sh 192.168.10.104 10ms 32
```
