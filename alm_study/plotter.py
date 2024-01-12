"""Plot ALM data."""

import argparse
import inspect
import itertools
import pathlib

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

import alm_study as alm
import alm_study.read_data as rd

module_dir = pathlib.Path(inspect.getfile(alm)).parents[0]
base_dir = module_dir.parents[0]
plt.style.use(module_dir / "project.mplstyle")
plt.rcParams.update({"figure.max_open_warning": 0})
prop_cycle = plt.rcParams["axes.prop_cycle"]
cmap = prop_cycle.by_key()["color"]
linestyles = prop_cycle.by_key()["linestyle"]
markers = itertools.cycle(("s", "d", "o", "p", "h"))


def export_plot_data(p, fname, xlabel="x", ylabel="y"):
    """Export plot data."""
    np.savetxt(
        fname,
        np.vstack((p.get_xdata(), p.get_ydata())).T,
        header=f"{xlabel} {ylabel}",
        comments="",
    )


def main():
    """Plot data."""
    parser = argparse.ArgumentParser(description="A simple plot tool")
    parser.add_argument(
        "-f", "--fdir", help="Folder with amr-wind data files", required=True, type=str
    )
    parser.add_argument(
        "-d", "--draw_blade", help="Draw the turbine blade", action="store_true"
    )
    args = parser.parse_args()

    uref = 8
    dref = 126
    # Force scale
    fs = dref * 1.23 * uref**2

    # The quantities of interest
    # others:
    # rd.QoiClass(index='Vy', label='Non-dimensional axial velocity ' + r'$U_x [-]$',),
    # rd.QoiClass(index='Fy', label='Force y$'),
    # rd.QoiClass(index='Phi', label='Flow angle ' + r'$\phi [-]$'),
    # rd.QoiClass(index='lift', label='lift'),
    # rd.QoiClass(index='drag', label='drag'),
    qois = [
        rd.QoiClass(
            index="Vx",
            label=r"$U_x (-)$",
            scale=1 / 8,
        ),
        rd.QoiClass(index="Fl", label=r"$L (-)$", scale=1 / fs),
        rd.QoiClass(index="Fd", label=r"$D (-)$", scale=1 / fs),
        rd.QoiClass(index="Alpha", label=r"$\alpha [^\circ]$"),
    ]

    # The location of all cases
    fdir = pathlib.Path(args.fdir)
    fname = fdir / "fast_inp" / "nrel5mw.out"

    # The list of all the cases
    times = [500, 1300]
    case_label = "AMR-Wind"
    case = rd.CaseClass(
        fname=fname,
        label=case_label,
        qois=qois,
        times=times,
    )

    ref_dir = base_dir / "refdata"
    refnames = {
        "JHU": {"label": "Johns Hopkins Code"},
        "KUL": {"label": "KU Leuven Code"},
        "NREL": {"label": "SOWFA"},
    }
    refmap = {"Vx": "Vaxial", "Alpha": "alpha", "Fl": "lift", "Fd": "drag"}

    # Loop and plot all the qoi along the blade
    fname = "plots.pdf"
    edir = base_dir / "plot_data"
    with PdfPages(fname) as pdf:
        blade_num = 0
        for qoi in qois:
            plt.figure(qoi.index)
            (p,) = plt.plot(
                case.r,
                case.qoi[blade_num][qoi.index],
                ls="-",
                marker=next(markers),
                label=case.label,
            )
            export_plot_data(p, edir / f"amr_wind_{qoi.index}.txt", ylabel=qoi.index)

            for k, v in refnames.items():
                x, y = np.loadtxt(
                    ref_dir / f"{k}_Data_{refmap[qoi.index]}", unpack=True
                )
                (p,) = plt.plot(
                    x, y, ls="-", marker=next(markers), label=v["label"], zorder=2
                )
                export_plot_data(p, edir / f"{k}_{qoi.index}.txt", ylabel=qoi.index)

            if args.draw_blade:
                rd.draw_blade(ref_dir / "blade_nrel5mw.png")

            plt.xlabel(r"$r(-)$")
            plt.ylabel(qoi.label)
            plt.gca().legend()
            pdf.savefig()


if __name__ == "__main__":
    main()
