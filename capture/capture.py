#!/usr/bin/env python3
import asyncio
from asyncio.futures import Future
import socketio
import numpy as np

sio = socketio.AsyncClient()


async def exec_remote(command):
    fut = asyncio.get_running_loop().create_future()
    await sio.emit("exec", command, callback=lambda _error, stdout, _stderr: fut.set_result(float(stdout.strip())))
    return await fut

async def set_exposure_ms(exposure):
    exposure_loc = "/axiom-api/devices/cmv12000/computed/exposure_time_ms/value"
    return await exec_remote(f"echo -n {exposure} > {exposure_loc}; cat {exposure_loc}")

async def set_gain(gain):
    gain_loc = "/axiom-api/devices/cmv12000/computed/analog_gain/value"
    return await exec_remote(f"echo -n {gain} > {gain_loc}; cat {gain_loc}")

async def do_work():
    for exposure in list(np.linspace(0.9, 1000 / 24, 50)) + list(np.logspace(np.log10(1000 / 24), np.log10(10000), 50)):
        for gain in range(1, 5):
            exposure = await set_exposure_ms(exposure)
            gain = await set_gain(gain)

            n = 1024 // max(1, int(round(np.log(exposure) / np.log(10))))

            proc = await asyncio.create_subprocess_shell("/data/projects/recorder/target/release/cli WebcamInput --device 4"
                              " ! DualFrameRawDecoder "
                              f" ! Average --n={n}"
                              f" ! RawBlobWriter --number-of-frames=1 --path darkframe_{gain}x_{exposure}ms_{n}n.blob")
            await proc.communicate()

async def main():
    await sio.connect('http://beta.lan')
    sio.start_background_task(do_work)
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(main())
