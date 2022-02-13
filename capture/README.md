# Prerequisites
* you need a recent Firmware 2.0 running on your AXIOM Beta.

# Usage
On the AXIOM Beta initialize the 4096 pixel wide raw mode with running the init script (as root) available from this repository instead of axiom_start.sh:
```
sudo su
2048_raw_init.sh
```

To capture an averaged frame on the AXIOM Recorder run:

```
./capture_calibration_frame.sh *Beta-IP* *exposure-time* *number-of-frames*
```

example:

```
./capture_calibration_frame.sh 192.168.10.104 10ms 32
```
