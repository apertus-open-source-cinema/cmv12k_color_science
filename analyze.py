#!/usr/bin/env python3

import numpy as np

import re
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import cm
from matplotlib.backends.backend_pdf import PdfPages

from raw_io import read_darkframes

import sys
from pathlib import Path

mpl.use('GTK3Agg')
plt.rcParams['figure.figsize'] = (20, 15)

filename = sys.argv[1]

m = re.search(r"_(\d)x_([0-9\.]+)(ms)?.blob", filename)
gain = float(m.group(1))
exposure_ms = float(m.group(2))


if sys.argv[2] == "means":
    darkframes = read_darkframes(filename)

    mean = np.mean(darkframes)
    std = np.std(darkframes)

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

    pdf = PdfPages(f"{Path(filename).with_suffix('.pdf')}")
    for n in plt.get_fignums():
        plt.figure(n).savefig(pdf, format="pdf")
    pdf.close()
    plt.close('all')
else:
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
