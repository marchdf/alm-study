"""Read ALM study data."""

# -*- coding: utf-8 -*-
#
#  interp_aerodyn_data.py
#
#  Copyright 2019 Martinez <lmartin1@LMARTIN1-31527S>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def draw_blade(blade_file="blade.png"):
    """Draw the blade in file."""
    # Read the blade image
    im = plt.imread(blade_file)

    # Get the limits
    ymin, ymax = plt.gca().get_ylim()

    dy = (ymax - ymin) * 0.1

    # Set the blade limit to 10% of the axis
    y2 = ymin - dy

    # ~ plt.imshow(im, aspect='auto', extent=[1.5/63, 1, y2, ymin],
    plt.imshow(
        im,
        aspect="auto",
        extent=[0, 1, y2, ymin],
        zorder=-1,
    )

    plt.ylim([y2, ymax])


class CaseClass:
    """A class that contains all the information for the cases."""

    def __init__(
        self,
        fname="nrel5mw.T1.out",
        nb=3,
        label="case",
        qoi_ls=None,
        times=None,
        color="blue",
        ls="-",
        marker=None,
        r0=1.5 / 63,
        r1=1,
    ):
        """Initialize."""
        # The file containing the openfast ascii output
        self.fname = fname

        # Number of blades
        self.nb = nb

        # The label used for plotting
        self.label = label

        # The list of quantities of interest
        self.qoi_ls = qoi_ls if qoi_ls is not None else []

        # The time to average the blade loads
        self.times = times if times is not None else [0, 100]

        # The plot parameters
        self.color = color
        self.ls = ls
        self.marker = marker

        #  Load the data as a pandas array
        self.df = pd.read_csv(
            fname,
            skiprows=[0, 1, 2, 3, 4, 5, 7],
            delim_whitespace=True,
            index_col=[0],
            error_bad_lines=False,
            # usecols=lambda x: 'B1N' in x,
        )
        # ~ for i in self.df.columns: print(i)

        # A list of all the nodes with Cl coefficient
        ls = [i for i in list(self.df.columns) if (("B1N" in i) & ("Phi" in i))]
        # The length of the list is the total number of actuator points
        self.N = len(ls)

        # The radial coordinate
        self.r = np.linspace(r0, r1, self.N)

        # An empty dictionary containing the averaged values
        self.qoi = [{} for n in range(self.nb)]

        # Extract all the quantities of interest
        self.extract_qoi(t=self.times)

    def extract_qoi(self, times=None):
        """Extract the data along the blade and average t -  the times to average."""
        if times is None:
            times = [0, 9999]
        for nb in range(self.nb):
            # Loop through all the quantities of interest and average
            for qoi in self.qoi_ls:

                # The list of all columns witht he given qoi
                ls = [
                    i
                    for i in list(self.df.columns)
                    if "B" + str(nb + 1) + "N" in i and i.endswith(qoi.index)
                ]

                # The index to identify time range
                index = (self.df.index >= times[0]) & (self.df.index <= times[1])

                # Take the mean of the given columns
                self.qoi[nb][qoi.index] = self.df[index][ls].mean() * qoi.scale


class QoiClass:
    """A class that contains all the information for the quantities of interest."""

    def __init__(self, index="Ft", label=r"$Ft$", scale=1.0):

        # The index used int he openfast file
        self.index = index

        # The label used in the plots
        self.label = label

        # The scale used to multiply the quantity
        self.scale = scale
