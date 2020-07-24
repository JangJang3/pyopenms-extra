import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QPointF
from pyqtgraph import PlotWidget
from nptyping import NDArray, Float, Int64
from typing import List, Any

pg.setConfigOption("background", "w")  # white background
pg.setConfigOption("foreground", "k")  # black peaks


class ErrorWidget(PlotWidget):
    """
    A class used to plot the difference between exact mass and theoretical
    mass.

    ...

    Attributes
    ----------
    mz : numpy array of floats
        The experimental mass-to-charge ratio (m/z) of the ions

    ppm : numpy array of floats
        Mass error of between experimental m/z and theoretical

    colors : numpy array of color tuples (r, g, b)
        Colors differentiate between prefix and suffix ions
        (prefix ions -> blue and suffix ions -> red)


    Methods
    -------
    setMassErrors(mz=ndarray, ppm=ndarray, colors=ndarray)
        Creates an error plot with mass spectrometry data

    redraw()
        Clears the plot of any data from previous settings and then draw the
        error plot with the given data

    """

    def __init__(self, *args):
        PlotWidget.__init__(self)

        self.setLimits(xMin=0)
        self.setLabel("bottom", "m/z")
        self.setLabel("left", "ppm")
        self._mzs = np.array([])
        self._ppm = np.array([])
        self._color_lib = np.array([])
        self.getViewBox().sigXRangeChanged.connect(self._autoscaleYAxis)
        self.setMouseEnabled(x=True, y=False)

    def setMassErrors(self, mz: NDArray[(Any, ...), Float],
                      ppm: NDArray[(Any, ...), Float],
                      colors: NDArray[(Any, ...), Int64]) -> None:
        """
        Creates an error plot with mass spectrometry data.

        Parameters
        ----------
        mz : numpy array of floats
            The experimental mass-to-charge ratio (m/z) of the ions

        ppm : numpy array of floats
            Mass error of between experimental m/z and theoretical

        colors : numpy array of color tuples (r, g, b)
            Colors differentiate between prefix and suffix ions
            (prefix ions -> blue and suffix ions -> red)

        """
        self._mzs = mz
        self._ppm = ppm
        self._color_lib = colors
        self.redraw()

    def redraw(self):
        """
        Clears the plot of any data from previous settings and then draws
        the error plot with the given data

        """
        self.plot(clear=True)
        self.setXRange(np.amin(self._mzs), np.amax(self._mzs))
        self._autoscaleYAxis()
        self._plotHorizontalLine()
        self._plotMassErrors()

    def _plotMassErrors(self):
        scattergraph = pg.ScatterPlotItem()
        points = []
        for i in range(0, self._ppm.size):
            points.append(
                {
                    "pos": (self._mzs[i], self._ppm[i]),
                    "brush": pg.mkBrush(self._color_lib[i]),
                }
            )
            scattergraph.addPoints(points)
            self.addItem(scattergraph)

    def _plotHorizontalLine(self):
        horizontalLine = pg.InfiniteLine(
            pos=QPointF(0.0, 0.0), angle=0, pen=pg.mkColor("k")
        )
        self.addItem(horizontalLine)

    def _autoscaleYAxis(self):
        x_range = self.getAxis("bottom").range
        if x_range == [0, 1]:  # workaround for axis sometimes not being set
            x_range = [np.amin(self._mzs), np.amax(self._mzs)]
        self.currMaxY = self._getMaxMassErrorInRange(x_range)
        if self.currMaxY:
            self.setYRange(self.currMaxY * (-1), self.currMaxY, update=False)

    def _getMaxMassErrorInRange(self, xrange: List[float, float]) -> Int64:
        """
        Finds the maximum mass error point in either experimental or
        theoretical data

        Parameters
        ----------
        xrange : List [float, float]
            The minimum and maximum mass-to-charge ratio (m/z) points currently
            presented in x-range of the plot


        Returns
        -------
        float
            The maximum mass error in the current x-range of both data
            
        """
        left = np.searchsorted(self._mzs, xrange[0], side="left")
        right = np.searchsorted(self._mzs, xrange[1], side="right")
        return np.amax(abs(self._ppm[left:right]), initial=1)
