"""Plot ALM data."""

import os

import matplotlib.pyplot as plt
import numpy as np

import alm_study.read_data as rd


def main():
    """Plot data."""
    uref = 8
    dref = 126
    # Force scale
    fs = dref * 1.23 * uref**2

    # The quantities of interest
    qoi_ls = [
        rd.QoiClass(
            index="Vx",
            label="Non-dimensional axial velocity " + r"$U_x [-]$",
            scale=1 / 8,
        ),
        #    rd.QoiClass(index='Vy',  label='Non-dimensional axial velocity ' + r'$U_x [-]$',),
        rd.QoiClass(index="Fl", label=r"$L_*$", scale=1 / fs),
        rd.QoiClass(index="Fd", label=r"$D_*$", scale=1 / fs),
        #    rd.QoiClass(index='Fy',  label='Force y$'),
        #    rd.QoiClass(index='Phi',  label='Flow angle ' + r'$\phi [-]$'),
        #    rd.QoiClass(index='lift',  label='lift'),
        #    rd.QoiClass(index='drag',  label='drag'),
        rd.QoiClass(index="Alpha", label="AoA"),
    ]

    # The location of all cases
    fname = (
        "/lustre/eaglefs/scratch/lmartine/amrwind_alm_nrel5MW_2/fast_inp/nrel5mw.out"
    )

    # The times to average
    times = [500, 1300]
    # times = [0.2, 0.2]

    # The list of all the cases
    cases = [
        rd.CaseClass(
            fname=fname,
            label="amr-wind",
            qoi_ls=qoi_ls,
            times=times,
            marker="o",
        ),
    ]

    out_dir = "alm_plots"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Loop and plot all the qoi along the blade
    for qoi in qoi_ls:

        plt.clf()
        # plt.figure(figsize=(16,6))

        # Loop thorugh all blades
        for i in range(1):

            plt.clf()

            # Loop through all cases
            for case in cases:

                plt.plot(
                    case.r,
                    case.qoi[i][qoi.index],
                    marker=case.marker,
                    # markevery=4,
                    ms=6,
                    ls=case.ls,
                    # color=case.color,
                    label="AMR-Wind",
                )

            #         if qoi.index=='AOA' or qoi.index == 'Phi':
            #             plt.ylim([4, 15])
            legend = {
                "JHU": "Johns Hopkins Code",
                "KUL": "KU Leuven Code",
                "NREL": "SOWFA",
            }

            for vars in [
                ["Vx", "Vaxial"],
                ["Alpha", "alpha"],
                ["Fl", "lift"],
                ["Fd", "drag"],
            ]:
                if qoi.index == vars[0]:
                    for label in ["JHU", "KUL", "NREL"]:
                        x, y = np.loadtxt(
                            "shareData/" + label + "_Data_" + vars[1], unpack=True
                        )
                        plt.plot(x, y, "o-", label=legend[label])

            rd.draw_blade("/home/lmartine/blade/blade_nrel5mw.png")

            xlabel = "non-dimensional blade radius [-]"
            ylabel = qoi.label

            plt.grid()
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.legend(bbox_to_anchor=(1.02, 0.5), loc="center left", ncol=1)

            plt.savefig(os.path.join(out_dir, qoi.index + ".pdf"), bbox_inches="tight")

            plt.show()


if __name__ == "__main__":
    main()
