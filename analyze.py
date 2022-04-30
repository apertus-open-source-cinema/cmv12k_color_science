#!/usr/bin/env python3

import numpy as np
import zarr

import re
from glob import glob
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import cm
from matplotlib.backends.backend_pdf import PdfPages

from raw_io import read_darkframes


# mpl.use('GTK3Agg')
plt.rcParams['figure.figsize'] = (20, 15)

def low_mem_std(arr, blocksize=1000000):
    num_blocks, remainder = divmod(len(arr), blocksize)
    mean = arr.mean()
    tmp = np.empty(blocksize, dtype=float)
    total_squares = 0
    for start in range(0, blocksize*num_blocks, blocksize):
        view = arr[start:start+blocksize]
        np.subtract(view, mean, out=tmp)
        tmp *= tmp
        total_squares += tmp.sum()
    if remainder:
        view = arr[-remainder:]
        tmp = tmp[-remainder:]
        np.subtract(view, mean, out=tmp)
        tmp *= tmp
        total_squares += tmp.sum()

    var = total_squares / len(arr)
    sd = var ** 0.5
    return sd


if sys.argv[1] == "exposure_analysis":
    means = {}
    for mean in glob("*.zarr"):
        z = zarr.open(mean)
        means[z]["gain"]
else:
    filename = sys.argv[1]

    m = re.search(r"_(\d)x_([0-9\.]+)(ms)?.blob", filename)
    gain = float(m.group(1))
    exposure_ms = float(m.group(2))
if sys.argv[2] in ["means", "by_color_means"]:
    all_darkframes = read_darkframes(filename)

    split_darkframes = [("all", all_darkframes)]
    if sys.argv[2] == "by_color_means":
        split_darkframes = [
            ("GB", all_darkframes[:,::2,::2]),
            ("B", all_darkframes[:,1::2,::2]),
            ("GR", all_darkframes[:,::2,1::2]),
            ("R", all_darkframes[:,1::2,1::2]),
        ]

    for name, darkframes in split_darkframes:
        mean = np.mean(darkframes)
        std = low_mem_std(np.ravel(darkframes))

        print(gain, exposure_ms, mean, std, darkframes.shape[0])

        bins = np.arange(int(mean - 3 * std), int(np.ceil(mean + 3 * std))) - 0.5
        plt.figure()
        plt.hist(np.ravel(darkframes), bins=bins)
        plt.title("histogram of all pixels")

        frame_mean = np.mean(darkframes, axis=0)

        plt.figure()
        plt.imshow(frame_mean.T, vmin = mean - 3 * std, vmax = mean + 3 * std)
        plt.colorbar()
        plt.tight_layout()
        plt.title("pixel-wise mean")

        column_mean = np.mean(frame_mean, axis=1, keepdims=True)
        frame_mean_by_column = frame_mean - column_mean
        mean = np.mean(frame_mean_by_column)
        std = np.std(frame_mean_by_column)

        plt.figure()
        plt.imshow(frame_mean_by_column.T, vmin = mean - 3 * std, vmax = mean + 3 * std, cmap='seismic')
        plt.colorbar()
        plt.tight_layout()
        plt.title("pixel-wise mean, subtracting the mean column offset")

        pdf = PdfPages(f"{Path(filename).with_suffix('.' + name + '.pdf')}")
        for n in plt.get_fignums():
            plt.figure(n).savefig(pdf, format="pdf")
        pdf.close()
        plt.close('all')
elif sys.argv[2] == "column_corrected_mean":
    darkframes = read_darkframes(filename, count=256)
    mean = np.mean(darkframes)
    std = np.std(darkframes)
    print(f"raw mean: {mean} +- {std}")
    frame_mean = np.mean(darkframes, axis=0)
    column_mean = np.mean(frame_mean, axis=1, keepdims=True)
    frame_mean_by_column = frame_mean - column_mean
    mean = np.mean(frame_mean_by_column)
    std = np.std(frame_mean_by_column)

    print(f"column corrected: {mean} +- {std}")
elif sys.argv[2] == "calculate_mean":
    darkframes = read_darkframes(filename, count=256)
    frame_mean = np.mean(darkframes, axis=0)


    # corrected_darkframes = (darkframes - frame_mean).astype(np.float32)
    # pdf = PdfPages(Path(filename).with_suffix('.single_frame_analysis.pdf'))
    # for i in range(10):
    #     df = corrected_darkframes[i]
    #     mean = np.mean(df)
    #     std = np.std(df)
    #     fig = plt.figure()
    #     plt.imshow(df.T, vmin = mean - 3 * std, vmax = mean + 3 * std, cmap='seismic')
    #     plt.colorbar()
    #     plt.tight_layout()
    #     plt.title(f"residual of frame {i}, mean = {mean} +- {std}")
    #     fig.savefig(pdf, format="pdf")
    #     plt.close('all')

    # for i in range(10):
    #     df = corrected_darkframes[i] - corrected_darkframes[i + 1]
    #     mean = np.mean(df)
    #     std = np.std(df)
    #     fig = plt.figure()
    #     plt.imshow(df.T, vmin = mean - 3 * std, vmax = mean + 3 * std, cmap='seismic')
    #     plt.colorbar()
    #     plt.tight_layout()
    #     plt.title(f"residual of frame {i} - {i + 1}, mean = {mean} +- {std}")
    #     fig.savefig(pdf, format="pdf")
    #     plt.close('all')
    # pdf.close()


    # print(gain, exposure_ms, low_mem_std(np.ravel(corrected_darkframes)))
    z = zarr.open(str(Path(filename).with_suffix(".mean.zarr")), mode="w", shape=frame_mean.shape, chunks=-1, dtype="f4")
    z.attrs["gain"] = gain
    z.attrs["exposure"] = exposure_ms
    z.attrs["source"] = filename
    z[:] = frame_mean
elif sys.argv[2] == "compress":
    import blosc2
    darkframes = read_darkframes(filename, count=128)
    Path("test.blosc2").write_bytes(blosc2.compress2(darkframes, typesize=2, clevel=3, compcode=blosc2.Codec.ZSTD, nthreads=12))
elif sys.argv[2] == "load":
    read_darkframes(filename)
elif sys.argv[2] == "unpack":
    outputdir = Path(filename).with_suffix("")
    outputdir.mkdir(exist_ok=True)
    for i, df in enumerate(darkframes):
        top = np.ravel(df[::2,:]).astype(np.uint8)
        bottom = np.ravel(df[1::2,:]).astype(np.uint8)
        print("top", top[0], top[1], top[2])
        print("bottom", bottom[0], bottom[1], bottom[2])
        (outputdir / f"{2 * i + 0:03}.blob").write_bytes(bottom.tobytes())
        (outputdir / f"{2 * i + 1:03}.blob").write_bytes(top.tobytes())


    # frame_mean = np.mean(darkframes, axis=0).astype(np.int16)
    # diffs = darkframes.astype(np.int16) - frame_mean

    # import zarr
    # from numcodecs import Zstd, Delta
    # filters = [Delta(dtype='i2')]
    # # compressor = Blosc(cname='zstd', clevel=9, shuffle=Blosc.AUTOSHUFFLE)
    # z = zarr.array(darkframes, chunks=-1, compressor=Zstd(level=9))
    # print("nominal size:", np.prod(darkframes.shape) * 12 // 8)
    # print(z.info)

    # darkframes = read_darkframes(filename, count=10)
    # frame_mean = np.mean(darkframes, axis=0)
    # diffs = darkframes.astype(np.int16) - frame_mean
    # print(np.min(diffs), np.max(diffs))
