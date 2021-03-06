"""This script plots IVCV files together for files generated by QTC
Data must be """

import logging
import holoviews as hv

from forge.tools import convert_to_df, rename_columns
from forge.tools import plot_all_measurements, convert_to_EngUnits
from forge.specialPlots import *


class Stripscan:
    def __init__(self, data, configs):

        self.log = logging.getLogger(__name__)
        self.config = configs
        self.analysisName = "Stripscan"
        self.data = convert_to_df(data, abs=self.config.get("abs_value_only", False))
        self.data = rename_columns(
            self.data,
            self.config.get(self.analysisName, {}).get("Measurement_aliases", {}),
        )
        self.finalPlot = None
        self.df = []
        self.measurements = self.data["columns"]
        self.donts = ()

        if "Pad" in self.measurements:
            padidx = self.measurements.index("Pad")
            self.xrow = "Pad"
        else:
            self.log.error("No 'Pad' column found in data. Analysis cannot be done!")
            return

        self.PlotDict = {"Name": self.analysisName}
        self.donts = ["Pad", "Name"]

        # Convert the units to the desired ones
        for meas in self.measurements:
            unit = (
                self.config[self.analysisName].get(meas, {}).get("UnitConversion", None)
            )
            if unit:
                self.data = convert_to_EngUnits(self.data, meas, unit)

    def run(self):
        """Runs the script"""

        # Plot all Measurements
        self.basePlots = plot_all_measurements(
            self.data, self.config, self.xrow, self.analysisName, do_not_plot=self.donts
        )
        self.PlotDict["BasePlots"] = self.basePlots
        self.PlotDict["All"] = self.basePlots

        # Plot all special Plots:
        # Histogram Plot
        self.Histogram = dospecialPlots(
            self.data,
            self.config,
            self.analysisName,
            "concatHistogram",
            self.measurements,
            **self.config[self.analysisName]
            .get("AuxOptions", {})
            .get("concatHistogram", {})
        )
        if self.Histogram:
            self.PlotDict["Histogram"] = self.Histogram
            self.PlotDict["All"] = self.PlotDict["All"] + self.Histogram

        # Whiskers Plot
        self.WhiskerPlots = dospecialPlots(
            self.data, self.config, self.analysisName, "BoxWhisker", self.measurements
        )
        if self.WhiskerPlots:
            self.PlotDict["Whiskers"] = self.WhiskerPlots
            self.PlotDict["All"] = self.PlotDict["All"] + self.WhiskerPlots

        # Violin Plot
        self.Violin = dospecialPlots(
            self.data, self.config, self.analysisName, "Violin", self.measurements
        )
        if self.Violin:
            self.PlotDict["Violin"] = self.Violin
            self.PlotDict["All"] = self.PlotDict["All"] + self.Violin

        # singleHist Plot
        self.singleHist = dospecialPlots(
            self.data,
            self.config,
            self.analysisName,
            "Histogram",
            self.measurements,
            **self.config[self.analysisName]
            .get("AuxOptions", {})
            .get("singleHistogram", {})
        )
        if self.singleHist:
            self.PlotDict["singleHistogram"] = self.singleHist
            self.PlotDict["All"] = self.PlotDict["All"] + self.singleHist

        # Reconfig the plots to be sure
        self.PlotDict["All"] = config_layout(
            self.PlotDict["All"], **self.config[self.analysisName].get("Layout", {})
        )
        self.PlotDict["data"] = self.data
        return self.PlotDict
