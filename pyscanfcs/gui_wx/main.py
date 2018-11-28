import csv
import os
import platform
import sys
import tempfile
import traceback
import webbrowser
import zipfile

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigureCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.widgets import RectangleSelector
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

import astropy.io.fits as pyfits
import multipletau
import numpy as np
from scipy.fftpack import fft
from scipy.fftpack import fftfreq
import wx.adv
from wx.lib.agw import floatspin
from wx.lib.scrolledpanel import ScrolledPanel

from .. import fitting
from .. import openfile
from .. import bin_pe
from .. import util

from . import doc
from . import edclasses
from . import misc
from . import uilayer



########################################################################
class ExceptionDialog(wx.MessageDialog):
    """"""

    def __init__(self, msg):
        """Constructor"""
        wx.MessageDialog.__init__(self, None, msg, "Error",
                                  wx.OK | wx.ICON_ERROR)


########################################################################
class plotarea(wx.Panel):
    def __init__(self, parent, grandparent):
        wx.Panel.__init__(self, parent, -1, size=(500, 500))
        # plotting area
        self.grandparent = grandparent
        self.figure = Figure()
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.axes = self.figure.add_subplot(111)
        #self.canvas.mpl_connect('button_press_event', self.on_pick)
        self.pdata = np.linspace(0, 100, 100)
        self.pdata.shape = (10, 10)
        self.image = self.axes.imshow(self.pdata, interpolation='nearest',
                                      cmap="gray", vmin=0, vmax=100)
        self.colorbar = self.figure.colorbar(self.image)
        # self.colorbar.set_ticks(np.arange(np.max(self.pdata)+1))
        self.colorbar.set_label("Photon events", size=16)
        self.toolbar = NavigationToolbar(self.canvas)
        # Set selector:
        self.rs = None
        self.UseLineSelector()
        # Layout:
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.toolbar, 0, wx.EXPAND)
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        # Labels
        self.axes.set_ylabel("Scan cycle time [ms]", size=16)
        self.axes.set_xlabel("Measurement time [s]", size=16)

    def OnSelectPlot(self, eclick, erelease):
        self.grandparent.OnSelectPlot(eclick, erelease)

    def UseLineSelector(self):
        lineprops = dict(color='red', linestyle='-',
                         linewidth=2, alpha=0.5)
        del self.rs
        self.rs = RectangleSelector(self.axes, self.OnSelectPlot, drawtype='line',
                                    lineprops=lineprops)

    def UseRectangleSelector(self):
        del self.rs
        rectprops = dict(facecolor='white', edgecolor='red',
                         alpha=0.2, fill=True)
        self.rs = RectangleSelector(self.axes, self.OnSelectPlot, drawtype='box',
                                    rectprops=rectprops)


########################################################################
class FFTmaxDialog(wx.Dialog):
    def __init__(
            self, parent, frequency, amplitude, size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE,
            useMetal=False,
    ):
        title = "Find maximum of Fourier Transform"
        wx.Dialog.__init__(self, parent, -1, title, pos, size, style)

        # Dialog conent
        # Text result
        self.pnt = parent
        self.ampl = amplitude / np.max(amplitude)
        self.freq = frequency * self.pnt.system_clock * 1e3
        self.label = wx.StaticText(self,
                                   label=" Click into the plot twice to define the interval where to search for the \
maximum. \n The data achieved will automatically be updated within the main program.\
\n You may close this window, when you are finished.")
        # plotting area
        self.figure = Figure()
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.axes = self.figure.add_subplot(111)

        self.axes.set_xlabel('Scan cycle [ms]')
        self.axes.set_ylabel('FFT signal')
        # We need x to be like that, because it represents the index of self.ampl
        #x = np.arange(len(self.ampl))
        self.freq[0] = 1
        x = 1 / self.freq

        self.image = self.axes.plot(x, self.ampl, '.', color="black")
        self.axes.set_xscale('log')
        self.axes.grid(True, which="major")
        self.axes.grid(True, which="minor")
        self.axes.yaxis.grid(False)
        self.toolbar = NavigationToolbar(self.canvas)
        self.canvas.mpl_connect('button_press_event', self.on_pick)

        # ipshell()
        #self.image.set_extent((self.freq[0], self.freq[1], np.min(self.ampl), np.max(self.ampl)))
        # Make the square or else we would not see much
        # self.plotarea.axes.set_aspect(1.*Tx/Ty)

        # Layout:
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.label, 0, wx.EXPAND)
        self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.toolbar, 0, wx.EXPAND)
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)

        self.counter = 0
        self.ymax = np.max(self.ampl)
        self.ymin = np.min(self.ampl)
        self.interval = [0, 0]
        self.red = False

        # Set window icon
        try:
            self.MainIcon = misc.getMainIcon()
            wx.Frame.SetIcon(self, self.MainIcon)
        except:
            self.MainIcon = None

    def on_pick(self, event):
        if (event.inaxes == self.axes and
                self.toolbar.mode == ""):
            # Let us draw some lines
            if self.counter == 0:
                self.line1 = self.axes.vlines(event.xdata, self.ymin,
                                              self.ymax, color='black')
                self.canvas.draw()
                self.counter = 1
            elif self.counter == 1:
                self.line2 = self.axes.vlines(event.xdata, self.ymin,
                                              self.ymax, color='black')
                self.canvas.draw()
                self.counter = 2
            elif self.counter == 2:
                self.line1._visible = False
                self.line1 = self.axes.vlines(event.xdata, self.ymin,
                                              self.ymax, color='black')
                self.canvas.draw()
                self.counter = 3
            elif self.counter == 3:
                self.line2._visible = False
                self.line2 = self.axes.vlines(event.xdata, self.ymin,
                                              self.ymax, color='black')
                self.canvas.draw()
                self.counter = 2
            # Transform time domain xdata to index for self.ampl
            newborder = 1 / event.xdata
            # The time domain should have large enough discretization.
            self.interval[0] = np.argwhere(
                (self.freq >= newborder) * (newborder > np.roll(self.freq, 1)))[0][0]
            self.interval[0], self.interval[1] = self.interval[1], self.interval[0]

            if self.counter >= 2:
                # Calculate maximum interval
                if self.red == True:
                    self.redline._visible = False
                    self.canvas.draw()
                self.red = True
                [start, stop] = [int(np.min(self.interval)) - 1,
                                 int(np.max(self.interval)) + 1]
                idx = np.argmax(self.ampl[start:stop]) + start
                # We now have the maximum, but we actually want to have some
                # kind of a weighted maximum. For that we take k data points next
                # to the maximum and weigth them with their relative amplitude.
                k = 10
                timeweights = list()
                timeweights.append(1 / self.freq[idx])
                Pie = 1
                for i in np.arange(k):
                    weighta = 1. * self.ampl[idx + i + 1] / self.ampl[idx]
                    weightb = 1. * self.ampl[idx - i - 1] / self.ampl[idx]
                    timeweights.append(weighta / self.freq[idx + i + 1])
                    timeweights.append(weightb / self.freq[idx - i - 1])
                    Pie = Pie + weighta + weightb
                    print(sum(np.array(timeweights)) / Pie, weighta, weightb)

                timeweights = np.array(timeweights)
                # print timeweights
                ltime = sum(timeweights) / Pie

                self.pnt.t_linescan = ltime * self.pnt.system_clock * 1e3

                #amplitudes = self.ampl[idx-k:idx+k]
                #frequencies = self.freq[idx-k:idx+k]
                self.redline = self.axes.vlines(
                    ltime, self.ymin, self.ymax, color='red')

                self.canvas.draw()
                # Plot the results
                # Set check box to True: "use cycle time"
                self.pnt.BoxPrebin[6].SetValue(True)
                self.pnt.Update()
                self.pnt.OnBinning_Prebin()


########################################################################
class MyFrame(wx.Frame):
    def __init__(self, parent, anid, version):
        # GUI exceptions
        sys.excepthook = MyExceptionHook

        self.version = version
        wx.Frame.__init__(self, parent, anid, "PyScanFCS " + self.version)
        self.CreateStatusBar()  # A Statusbar in the bottom of the window

        # Properties of the Frame
        if sys.platform == "darwin":
            initial_size = (1036, 622)
        else:
            initial_size = (1024, 595)
        #initial_size = (1024,768)
        self.SetSize(initial_size)
        self.SetMinSize(initial_size)

        # Set this, so we know in which directory we are working in.
        # This will change, when we load a data file.
        self.dirname = os.curdir
        self.filename = ''

        self.MakeMenu()

        # Create the initial windows
        # When the user opens a file via file menu, the first 1e+6 datapoints
        # will be generated (binned) and plotted. We do not need to do this,
        # but it makes the program more transparent. Then we will need to find
        # the repetition time (time needed to scan one line) and bin the whole
        # thing accordingly and plot again.

        self.sp = wx.SplitterWindow(self, style=wx.SP_3DSASH)
        self.buttonarea = ScrolledPanel(self.sp)
        self.buttonarea.SetupScrolling(scroll_y=True)
        self.plotarea = plotarea(self.sp, self)
        self.pdata = np.linspace(0, 1, 100)
        self.pdata.shape = (10, 10)
        #self.plotarea = wxmplot.ImagePanel(self.sp)
        # self.plotarea.display(self.pdata)

        self.MakeButtons()

        self.Layout()

        split = max(400, self.firhorz.GetMinSize()[0] + 5)
        self.sp.SplitVertically(self.buttonarea, self.plotarea, split)

        self.Show()

        # Initial data values:
        # Time values are system clock ticks
        # System clock in MHz
        self.system_clock = None
        self.T_total = None
        self.t_linescan = None
        self.t_bin = None
        self.datData = None
        self.intData = None
        self.bins_per_line = None
        self.percent = 0.  # correction factor for cycle time

        # A square displayed upon selection:
        self.square = None
        self.squareB = None
        # Coordinates of the square [(x1, x2), (y1,y2)]
        self.XY_Trace_square = [(None, None), (None, None)]
        self.XY_Trace_squareB = [(None, None), (None, None)]

        # List of absolute filenames that contain bleaching info
        self.file_bleach_profile = list()

        # Temporary filenames for binned intensity
        self.tempbintot = tempfile.mktemp("_binned_total.int")
        self.tempbinpar = tempfile.mktemp("_binned_partial.int")

        # We try to work with a cache to save time.
        self.cache = dict()
        # Each element of the cache is a filename connected to some data
        # cachetest = self.cache["testA.dat"] = dict()
        # cachetest["bins_per_line"] = self.bins_per_line
        # cachetest["linetime"] = self.t_linescan
        # cachetest["data"] = self.intData
        self.Update()
        # Set window icon
        try:
            self.MainIcon = misc.getMainIcon()
            wx.Frame.SetIcon(self, self.MainIcon)
        except:
            self.MainIcon = None
        
        if hasattr(sys, "frozen"):
            self.OnMenuSupport()


    def AddToCache(self, Data, cachename, background=False):
        if list(self.cache.keys()).count(cachename) == 0:
            # Add the menu entry
            menu = self.cachemenu.Append(
                wx.ID_ANY, cachename, kind=wx.ITEM_RADIO)
            if background == False:
                # If True, do not activate new menu.
                menu.Check(True)
            # OnSelectCache plots the selected Cache element
            self.Bind(wx.EVT_MENU, self.OnSelectCache, menu)
        acache = dict()
        acache["data"] = 1 * Data
        acache["bins_per_line"] = self.bins_per_line
        acache["linetime"] = self.t_linescan
        acache["dirname"] = self.dirname
        self.cache[cachename] = acache

    def Bin_All_Photon_Events(self, Data):
        """ Bin all photon events according to a binsize t_bin.
        """
        eb = self.BoxPrebin[10].GetValue()  # 10 spin: bin shift
        # The box contains bins per line
        self.bins_per_line = int(self.BoxPrebin[8].GetValue())
        # t_bin in clock ticks
        t_bin = self.t_linescan / self.bins_per_line
        outdtype = np.uint16
        outfile = self.tempbintot

        wxdlg = uilayer.wxdlg(parent=self, steps=100,
                              title="Binning photon events...")

        print("Creating file {} ({})".format(outfile, outdtype.__name__))

        bin_pe.bin_photon_events(Data, t_bin, binshift=eb,
                                 outfile=outfile,
                                 outdtype=outdtype,
                                 callback=wxdlg.Iterate)
        wxdlg.Finalize()

        binneddata = np.fromfile(outfile, dtype=outdtype)

        if np.max(binneddata) < 256:
            # save memory
            binneddata = np.uint8(binneddata)
        return binneddata

    def Bin_Photon_Events(self, n_events=None, t_bin=None):
        """
        Given an array of time differences *Data* [µs] between photon events, 
        calculate the photon events that take place every *t_bin* in system 
        clocks, where n_events is the number of events to use.
        """
        # The box contains bins per line
        self.bins_per_line = int(self.BoxPrebin[8].GetValue())

        # t_bin in clock ticks
        self.t_bin = t_bin
        outdtype = np.uint16
        outfile = self.tempbinpar
        eb = self.BoxPrebin[10].GetValue()  # 10 spin: bin shift

        Data = self.datData[:n_events]

        wxdlg = uilayer.wxdlg(parent=self, steps=100,
                              title="Binning photon events...")

        print("Creating file {} ({})".format(outfile, outdtype.__name__))

        bin_pe.bin_photon_events(Data, t_bin, binshift=eb,
                                   outfile=outfile,
                                   outdtype=outdtype,
                                   callback=wxdlg.Iterate)
        wxdlg.Finalize()

        binneddata = np.fromfile(outfile, dtype=outdtype)

        if np.max(binneddata) < 256:
            # save memory
            binneddata = np.uint8(binneddata)

        return binneddata

    def CorrectLineTime(self, event):
        percent = np.float(self.linespin.GetValue())
        if self.t_linescan is not None:
            # Set the new linetime
            self.t_linescan = np.float(self.t_linescan) * (1. + percent / 100.)
            self.percent = percent
            self.UpdateInfo()

    def GetTotalTime(self):
        """ 
        Sums over self.datData to find out the total time of the measurement.
        Sets variable self.T_total
        """
        # Need to set float variable here, because uint32 are not
        # large enough. T_total in system clocks.
        self.T_total = np.sum(self.datData, dtype="float")
        self.Update()

    def GetTraceFromIntData(self, intData, coords, title="Trace"):
        """
            region is a number describing the region the trace comes from (1 or 2)
        """
        # Get the data
        # Make sure we have the corners of the square
        for atuple in coords:
            if atuple[0] is None or atuple[1] is None:
                return
        [(x1, x2), (y1, y2)] = coords

        # Convert times to positions in 2D array
        x1 = int(np.floor(x1 / self.t_linescan))
        x2 = int(np.ceil(x2 / self.t_linescan))
        y1 = int(np.floor(y1 / self.t_bin))
        y2 = int(np.ceil(y2 / self.t_bin))
        bins_in_col = y2 - y1
        bins_in_row = x2 - x1

        # Get some needed data
        # bin time for on line in s (used for multiple tau algorithm)
        bintime = self.t_linescan / self.system_clock / 1e6
        # Number of bins next to the maximum to use for the trace
        num_next_max = self.Spinnumax.GetValue()

        # We have to swap x and y, because we want to access
        # the array linewise later.
        traceData = np.zeros((bins_in_row, bins_in_col))

        # We start from x1 (lowest time available) and
        # successively fill the traceData array:
        pos = x1 * self.bins_per_line
        for i in np.arange(len(traceData)):
            traceData[i] = intData[pos + y1:pos + y2]
            pos = pos + self.bins_per_line

        # Get the actual trace
        # Calculate trace from maximum
        traceDataMaxids = np.argmax(traceData, axis=1)
        newtraceData = np.zeros((len(traceDataMaxids), num_next_max * 2 + 1))

        for i in np.arange(len(traceData)):
            # We add to the new trace data array, such that the maximum of
            # each line is at the center of the array.
            maid = traceDataMaxids[i]
            # The array to be written to newtraceData
            nsli = np.zeros(num_next_max * 2 + 1)
            nsli[num_next_max] = traceData[i][maid]
            for k in np.arange(num_next_max) + 1:
                if maid + 1 - k >= 0:
                    nsli[num_next_max - k] = traceData[i][maid - k]
                if maid + 1 + k <= len(traceData[i]):
                    nsli[num_next_max + k] = traceData[i][maid + k]
            newtraceData[i] = nsli
        del traceDataMaxids

        if self.CheckBoxCountrateFilter.GetValue() is True:
            # "temporal detection profile"
            # We use this to find out how much time we spent in the membrane
            detprof = np.sum(newtraceData, axis=0)

            # Countrate correction:
            x = np.linspace(-num_next_max, +num_next_max, len(detprof))
            popt, gauss = fitting.fit_gauss(
                detprof, x, np.argmax(detprof))
            # Time in bins, that the focus effectively was inside the membrane:
            # Go two sigmas in each direction. This way we have an averaged
            # cpp in the end.
            MembraneBins = 4 * popt[2]
            LinetimeBins = self.bins_per_line

            #tracemean = np.mean(newtraceData)
            self.TraceCorrectionFactor = LinetimeBins / MembraneBins

            if self.MenuVerbose.IsChecked():
                x2 = np.linspace(popt[0] - 4 * popt[2],
                                 popt[0] + 4 * popt[2], 100)
                plt.figure()
                plt.subplot(111)
                plt.plot(x, detprof, "-", label="Measured profile")
                plt.plot(x2, gauss(popt, x2), "-", label="Gaussian fit")
                plt.legend()
                text = "sigma = " + str(popt[2]) + " bins\n" +\
                       "residence time in bins: " + str(MembraneBins) + "\n" +\
                       u"residence time [µs]: " + str(MembraneBins * bintime * 1e6 /
                                                      self.bins_per_line)
                coords = (MembraneBins, np.max(detprof) / 2.)
                plt.text(coords[0], coords[1], text)
                plt.xlabel("Bin position relative to maximum in cycle time")
                plt.ylabel("Sum of counted photons (whole trace)")
                plt.title(
                    title + " - Determination of residence time in membrane")
                plt.show()
        else:
            self.TraceCorrectionFactor = 1.

        # We could multiply newtraceData with self.TraceCorrectionFactor right
        # here, but we are not doing it, because it might introduce numerical
        # errors. This does not change statistics. In order to get the correct
        # countrate, we correct the traces, when they are binned for saving
        # in .csv files.
        newtraceData = np.sum(newtraceData, axis=1)
        traceData = newtraceData

        # Bleach filter?
        if self.CheckBoxBleachFilter.GetValue() is True:
            ltrb = len(traceData)
            # Perform bleaching correction
            # fitted function:
            # f_i = f_0 * exp(-t_i/t_0) + offset
            # parms = [f_0, t_0, offset]
            # Corrected function:
            # F_c = F_i/(f_0*exp(-ti/(2*t_0))) + f_0*(1-f_0*exp(-t_i/(2*t_0)))
            # We don't want to subtract an offset from the trace?
            # The offset is actually background signal.
            popt, expfunc = fitting.fit_exp(np.arange(len(traceData)),
                                            traceData)
            [f_0, t_0] = popt

            newtrace = util.reduce_trace(traceData, bintime,
                                               length=500)

            # Full trace:
            ti = np.arange(ltrb)
            expfull = np.exp(-ti / (2 * t_0))
            # see formula above:
            traceData = traceData / expfull + f_0 * (1 - expfull)

            # TODO:
            # Does this do anything?
            newtracecorr = util.reduce_trace(traceData, bintime, length=500)

            fitfuncdata = expfunc(popt, np.arange(ltrb))
            newtracefit = util.reduce_trace(fitfuncdata, bintime, length=500)

            # Bleaching profile to temporary file
            # Create a temporary file and open it
            filename = tempfile.mktemp(".csv",
                                       "PyScanFCS_bleach_profile_{}_".format(
                                           title.replace(" ", "_")))
            with open(filename, 'w') as fd:
                fd.write("# This is not correlation data.\r\n")
                fd.write("# {} - bleaching correction\r\n".format(title))
                fd.write(
                    "# I = ({:.2e})*exp[-t / (2*({:.2e})) ]\r\n".format(f_0, t_0))
                fd.write("# {}\t{}\t{}\t{}\r\n".format(u"Time t [s]",
                                                            u"Measured trace [kHz]", u"Exponential fit I [kHz]",
                                                            u"Corrected trace [kHz]"))
                dataWriter = csv.writer(fd, delimiter='\t')
                # we will write
                xexp = newtrace[:, 0]
                yexp = newtrace[:, 1] * self.TraceCorrectionFactor
                yfit = newtracefit[:, 1] * self.TraceCorrectionFactor
                ycorr = newtracecorr[:, 1] * self.TraceCorrectionFactor
                data = [xexp, yexp, yfit, ycorr]
                for i in np.arange(len(data[0])):
                    # row-wise, data may have more than two elements per row
                    datarow = list()
                    for j in np.arange(len(data)):
                        rowcoli = str("%.10e") % data[j][i]
                        datarow.append(rowcoli)
                    dataWriter.writerow(datarow)

            self.file_bleach_profile.append(filename)

            if self.MenuVerbose.IsChecked():
                def view_bleach_profile(e=None):
                    # Open the file
                    if platform.system().lower() == 'windows':
                        os.system("start /b " + filename)
                    elif platform.system().lower() == 'linux':
                        os.system("xdg-open " + filename + " &")
                    elif platform.system().lower() == 'darwin':
                        os.system("open " + filename + " &")
                    else:
                        # defaults to linux style:
                        os.system("xdg-open " + filename + " &")
                # Show a plot

                #fig, ax = plt.figure()
                #ax = plt.subplot(111)
                plt.subplots()
                plt.subplots_adjust(bottom=0.2)
                plt.title(title + " - bleaching correction")
                plt.xlabel("Measurement time t [s]")
                plt.ylabel("approx. Intensity I [kHz]")
                plt.plot(xexp, yexp, '-',
                         label="Measured trace", color="gray")
                plt.plot(xexp, yfit, '-',
                         label="Exponential fit", color="red")
                plt.plot(xexp, ycorr, '-',
                         label="Corrected trace", color="blue")
                xt = np.min(xexp)
                yt = np.min(yexp)
                text = "I = ({:.2e})*exp[-t / (2*({:.2e})) ]".format(f_0, t_0)
                plt.text(xt, yt, text, size=12)
                plt.legend()
                plt.show()

                # We would like to have a button for the view_bleach_profile
                # function. Unfortunately, this does not work:
                #axgb = plt.axes([0.75, 0.05, 0.15, 0.05])
                #buttonbleach = Button(axgb, 'view data')
                # buttonbleach.on_clicked(view_bleach_data)
                view_bleach_profile()
        return traceData

    def MakeButtons(self):
        minsize = (150, -1)
        dropminsize = (175, -1)
        # Pre-binning
        prebox = wx.StaticBox(self.buttonarea, label="Pre-binning")
        presizer = wx.StaticBoxSizer(prebox, wx.VERTICAL)
        # Checkbox for later using the cycle time
        precheck = wx.CheckBox(self.buttonarea, label="Use cycle time")
        precheck.Bind(wx.EVT_CHECKBOX, self.Update)
        precheck.IsChecked = False
        presizer.Add(precheck)
        # Text bins per line
        prebplt = wx.StaticText(self.buttonarea, -1, "Bins per scan cycle:")
        presizer.Add(prebplt)
        # Bins per line
        self.prebpl = wx.SpinCtrl(self.buttonarea, -1, min=1, max=50000,
                                  value="70")
        self.prebpl.SetMinSize(minsize)
        presizer.Add(self.prebpl)
        # Text bins
        pretext = wx.StaticText(self.buttonarea, -1, "No. of events to use:")
        presizer.Add(pretext)
        # Spin bins
        prespin = wx.SpinCtrl(self.buttonarea, -1, min=100,
                              max=500000000, value="1000")
        prespin.SetMinSize(minsize)
        presizer.Add(prespin)
        # Text tbin
        pretextt = wx.StaticText(self.buttonarea, -1, u"Bin width [µs]:")
        presizer.Add(pretextt)
        # Spin tbin
        prespint = edclasses.FloatSpin(self.buttonarea, value="5.0")
        prespint.SetMinSize(minsize)
        presizer.Add(prespint)
        # Text binfshift
        preshifttextt = wx.StaticText(self.buttonarea, -1, "Bin shift:")
        presizer.Add(preshifttextt)
        # Spin shift bins
        prespinshift = wx.SpinCtrl(self.buttonarea, -1, min=0,
                                   max=500000000, value="0")
        prespinshift.SetMinSize(minsize)
        presizer.Add(prespinshift)
        # Button
        prebutt = wx.Button(self.buttonarea, label="Calculate and plot")
        self.Bind(wx.EVT_BUTTON, self.OnBinning_Prebin, prebutt)
        presizer.Add(prebutt)
        self.BoxPrebin = list()
        self.BoxPrebin.append(prebox)       # 0 box
        self.BoxPrebin.append(pretext)      # 1 text: enter # events to use
        self.BoxPrebin.append(prespin)      # 2 spin: how many bins to bin
        self.BoxPrebin.append(pretextt)     # 3 text: enter bind width
        self.BoxPrebin.append(prespint)     # 4 spin: bin time
        self.BoxPrebin.append(prebutt)      # 5 button
        self.BoxPrebin.append(precheck)     # 6 checkbox: use linetime
        self.BoxPrebin.append(prebplt)      # 7 text: bins per line
        self.BoxPrebin.append(self.prebpl)  # 8 spin: bins per line
        self.BoxPrebin.append(preshifttextt)  # 9 text: bin shift
        self.BoxPrebin.append(prespinshift)  # 10 spin: bin shift

        # Total-binning
        binbox = wx.StaticBox(self.buttonarea, label="Total-binning")
        binsizer = wx.StaticBoxSizer(binbox, wx.VERTICAL)
        # Some informative text
        bintext = wx.StaticText(self.buttonarea, -1, "Bin entire file.")
        binsizer.Add(bintext)
        # OK button
        binbutt = wx.Button(self.buttonarea, label="Calculate and plot all")
        self.Bind(wx.EVT_BUTTON, self.OnBinning_Total, binbutt)
        binsizer.Add(binbutt)
        self.BoxBinTotal = [binbox, bintext, binbutt]

        # Mode
        modebox = wx.StaticBox(self.buttonarea, label="Mode")
        modesizer = wx.StaticBoxSizer(modebox, wx.VERTICAL)
        # Some informative text
        bintext = wx.StaticText(self.buttonarea, -1, "Type of measurement.")
        modesizer.Add(bintext)
        # Dropdown mode selection
        Modelist = ["1 colour 1 focus", "2 colours 1 focus", "1 colour 2 foci",
                    "2 colours 2 foci", "Alternating excitation"]
        self.ModeDropDown = wx.ComboBox(self.buttonarea, -1, "", (15, 30),
                                        wx.DefaultSize, Modelist, wx.CB_DROPDOWN)
        self.ModeDropDown.SetMinSize(dropminsize)
        self.ModeDropDown.SetSelection(0)
        self.Bind(wx.EVT_COMBOBOX, self.Update, self.ModeDropDown)
        modesizer.Add(self.ModeDropDown)
        # Save trace checkbox
        self.CheckBoxSaveTrace = wx.CheckBox(self.buttonarea, -1,
                                             label="Save raw traces")
        self.CheckBoxSaveTrace.SetValue(False)
        modesizer.Add(self.CheckBoxSaveTrace)

        # Data
        infobox = wx.StaticBox(self.buttonarea, label="Data")
        insizer = wx.StaticBoxSizer(infobox, wx.VERTICAL)
        sclock = wx.StaticText(self.buttonarea, -1,
                               "System clock [MHz]: \t \t")
        insizer.Add(sclock)
        totalt = wx.StaticText(self.buttonarea, -1,
                               "Total time [s]:  \t \t")
        insizer.Add(totalt)
        linet = wx.StaticText(self.buttonarea, -1, "Scan cycle [ms]:")
        insizer.Add(linet)
        linetdropdown = wx.ComboBox(self.buttonarea, -1, "", (15, 30),
                                    wx.DefaultSize, [], wx.CB_DROPDOWN)
        linetdropdown.SetMinSize(dropminsize)
        insizer.Add(linetdropdown)
        self.Bind(wx.EVT_COMBOBOX, self.OnLinetimeSelected,
                  linetdropdown)
        self.Bind(wx.EVT_TEXT, self.OnLinetimeSelected, linetdropdown)
        # Do not change order of BoxInfo!!
        self.BoxInfo = [sclock, totalt, linetdropdown, infobox, linet]

        # Scan cycle periodicity
        lscanbox = wx.StaticBox(self.buttonarea,
                                label="Scan cycle periodicity")
        lscansizer = wx.StaticBoxSizer(lscanbox, wx.VERTICAL)
        # Magic checkbox
        lscanmagic = wx.CheckBox(self.buttonarea,
                                 label="Find automagically")
        lscanmagic.SetValue(True)
        lscansizer.Add(lscanmagic)
        # OK button
        lscanbutt = wx.Button(self.buttonarea,
                              label="Find periodicity (FFT)")
        self.Bind(wx.EVT_BUTTON, self.OnFindLineScanTime, lscanbutt)
        lscansizer.Add(lscanbutt)
        self.BoxLineScan = [lscanbox, lscanmagic, lscanbutt]

        # Image selection
        # Add radio buttons that change behavior of mouse in Plot
        userbox = wx.StaticBox(self.buttonarea, label="Image selection")
        usizer = wx.StaticBoxSizer(userbox, wx.VERTICAL)
        self.RbtnLinet = wx.RadioButton(self.buttonarea, -1,
                                        'Scan cycle correction % +/-: ', style=wx.RB_GROUP)
        self.linespin = floatspin.FloatSpin(self.buttonarea, digits=10,
                                            increment=.001)
        self.linespin.SetMinSize(minsize)
        self.linespin.Bind(wx.EVT_SPINCTRL, self.CorrectLineTime)
        self.RbtnSelect = wx.RadioButton(self.buttonarea, -1,
                                         'Select region 1')
        self.RbtnSelectB = wx.RadioButton(self.buttonarea, -1,
                                          'Select region 2')
        self.RbtnLinet.SetValue(True)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioSelector,
                  self.RbtnSelect)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioSelector,
                  self.RbtnSelectB)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioSelector,
                  self.RbtnLinet)
        # version 0.2.2: Add button "full measurement time"
        fullmeasbutt = wx.Button(self.buttonarea,
                                 label="Full measurement time")
        self.Bind(wx.EVT_BUTTON, self.OnSetFullMeasTime, fullmeasbutt)
        usizer.Add(self.RbtnLinet)
        usizer.Add(self.linespin)
        usizer.Add(self.RbtnSelect)
        usizer.Add(self.RbtnSelectB)
        usizer.Add(fullmeasbutt)
        self.BoxImageSelection = [userbox, self.RbtnLinet,
                                  self.linespin, self.RbtnSelect, self.RbtnSelectB, fullmeasbutt]

        # Correlation
        corrbox = wx.StaticBox(self.buttonarea, label="Correlation")
        corrsizer = wx.StaticBoxSizer(corrbox, wx.VERTICAL)
        # Add switch for
        # how many bins next to a maximum should be used for the trace
        corrsizerText1 = wx.StaticText(self.buttonarea,
                                       label="Span +/-:")
        corrsizer.Add(corrsizerText1)
        self.Spinnumax = wx.SpinCtrl(self.buttonarea, -1, min=0,
                                     max=50000, value="3")
        self.Spinnumax.SetMinSize(minsize)
        corrsizer.Add(self.Spinnumax)
        # Add switch for slicing of trace
        corrsizerText3 = wx.StaticText(self.buttonarea,
                                       label="No. of trace slices:")
        corrsizer.Add(corrsizerText3)
        self.Spinslice = wx.SpinCtrl(self.buttonarea, -1, min=1,
                                     max=50000, value="10")
        self.Spinslice.SetMinSize(minsize)
        corrsizer.Add(self.Spinslice)
        # Trace
        # Switch for bleaching correction
        self.CheckBoxBleachFilter = wx.CheckBox(self.buttonarea, -1,
                                                label="Bleach filter")
        self.CheckBoxBleachFilter.SetValue(True)
        corrsizer.Add(self.CheckBoxBleachFilter)
        # Switch for countrate correction
        self.CheckBoxCountrateFilter = wx.CheckBox(self.buttonarea, -1,
                                                   label="Countrate filter")
        self.CheckBoxCountrateFilter.SetValue(False)
        corrsizer.Add(self.CheckBoxCountrateFilter)
        # Add switch for m
        # m is the parameter that defines the number of channels
        # after which the the intensity trace is binned (neighboring
        # pixels are combined) for calculation of the
        # correlation function on a semi-logarithmic scale.
        corrsizerText2 = wx.StaticText(self.buttonarea,
                                       label=u"M.-τ parameter m:")
        corrsizer.Add(corrsizerText2)
        self.Spinm = wx.SpinCtrl(self.buttonarea, -1, min=16, max=50000,
                                 value="16")
        self.Spinm.SetMinSize(minsize)
        corrsizer.Add(self.Spinm)
        # Multiple Tau
        # Get Autocorrelation function
        taubutt = wx.Button(self.buttonarea, label="Get correlation")
        self.Bind(wx.EVT_BUTTON, self.OnMultipleTau, taubutt)
        corrsizer.Add(taubutt)
        self.BoxMultipleTau = [self.CheckBoxBleachFilter, corrbox,
                               corrsizerText3, corrsizerText1, self.Spinnumax,
                               corrsizerText2, self.Spinm, self.Spinslice, taubutt,
                               self.CheckBoxCountrateFilter]

        # Set sizes
        firlist = [presizer, binsizer, modesizer]
        firmin = 100
        for abox in firlist:
            firmin = max(abox.GetMinSize()[0], firmin)
        for abox in firlist:
            abox.SetMinSize((firmin, -1))
        seclist = [corrsizer, usizer, lscansizer, insizer]
        secmin = 100
        for abox in seclist:
            secmin = max(abox.GetMinSize()[0], secmin)
        for abox in seclist:
            abox.SetMinSize((secmin, -1))

        # Put everything together
        self.firvert = wx.BoxSizer(wx.VERTICAL)
        self.firvert.Add(presizer)
        self.firvert.AddSpacer(5)
        self.firvert.Add(binsizer)
        self.firvert.AddSpacer(5)
        self.firvert.Add(modesizer)
        self.secvert = wx.BoxSizer(wx.VERTICAL)
        self.secvert.Add(insizer)
        self.secvert.AddSpacer(5)
        self.secvert.Add(lscansizer)
        self.secvert.AddSpacer(5)
        self.secvert.Add(usizer)
        self.secvert.AddSpacer(5)
        self.secvert.Add(corrsizer)
        self.firhorz = wx.BoxSizer(wx.HORIZONTAL)
        self.firhorz.AddSpacer(5)
        self.firhorz.Add(self.firvert)
        self.firhorz.AddSpacer(5)
        self.firhorz.Add(self.secvert)
        self.buttonarea.SetSizer(self.firhorz)

    def MakeMenu(self):
        # Setting up the menus.
        filemenu = wx.Menu()
        self.cachemenu = wx.Menu()
        prefmenu = wx.Menu()
        helpmenu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        # filemenu
        menuOpenDat = filemenu.Append(wx.ID_OPEN, "&Open photon events file",
                                      "Opens a correlator file (e.g. .dat) that contains photon arrival time differences")
        menuOpenFits = filemenu.Append(wx.ID_ANY, "Open &binned data file",
                                       "Opens a previously binned intensity file (.fits)")
        self.menuSaveDat = filemenu.Append(wx.ID_ANY, "Save 32 bit .&dat file",
                                           "Saves photon arrival time difference data in 32 bit file format")
        self.menuSaveFits = filemenu.Append(wx.ID_SAVE, "&Save .fits file",
                                            "Saves binned intensity data into a .fits file")
        filemenu.AppendSeparator()
        menuTest = filemenu.Append(
            wx.ID_ANY, "Create &artificial .dat file", "Create an artificial data set")
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(
            wx.ID_EXIT, "E&xit", "Terminate the program")

        # prefmenu
        self.MenuVerbose = prefmenu.Append(wx.ID_ANY, "Verbose mode",
                                           "Enables/Disables output of additional information.",
                                           kind=wx.ITEM_CHECK)
        # Check by default
        self.MenuVerbose.Check()

        menuSupport = helpmenu.Append(wx.ID_ANY, "&Support",
                                   "Contributing and getting support")
        menuDocu = helpmenu.Append(wx.ID_ANY, "&Documentation",
                                   "PyCorrFit documentation")
        menuWiki = helpmenu.Append(wx.ID_ANY, "&Wiki",
                                   "PyCorrFit wiki pages by users for users (online)")
        helpmenu.AppendSeparator()
        menuSoftw = helpmenu.Append(wx.ID_ANY, "&Software used",
                                    "Information about software used by this program")
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About",
                                    "Information about this program")

        # Creating the menubar.
        self.menuBar = wx.MenuBar()
        # Adding the "filemenu" to the MenuBar
        self.menuBar.Append(filemenu, "&File")
        self.menuBar.Append(self.cachemenu, "&Cache")
        self.menuBar.Append(prefmenu, "&Preferences")
        self.menuBar.Append(helpmenu, "&Help")

        # Adding the MenuBar to the Frame content.
        self.SetMenuBar(self.menuBar)

        # Set events
        # File
        self.Bind(wx.EVT_MENU, self.OnMenuExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnOpenStream, menuOpenDat)
        self.Bind(wx.EVT_MENU, self.OnOpenBinned, menuOpenFits)
        self.Bind(wx.EVT_MENU, self.OnSaveDat, self.menuSaveDat)
        self.Bind(wx.EVT_MENU, self.OnSaveFits, self.menuSaveFits)
        self.Bind(wx.EVT_MENU, self.OnMenuTest, menuTest)

        # Help
        self.Bind(wx.EVT_MENU, self.OnMenuSupport, menuSupport)
        self.Bind(wx.EVT_MENU, self.OnMenuAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnMenuSoftware, menuSoftw)
        self.Bind(wx.EVT_MENU, self.OnMenuDocumentation, menuDocu)
        self.Bind(wx.EVT_MENU, self.OnMenuWiki, menuWiki)

    def OnBinning_Prebin(self, event=None):
        """ Do prebinngin using *Bin_Photon_Events()* """
        n_events = self.BoxPrebin[2].GetValue()
        if self.BoxPrebin[6].GetValue() == False:
            # from µs tp system clock ticks
            t_bin = self.BoxPrebin[4].GetValue() * self.system_clock
            # If, reset previously achieved things. # - Why?
            # self.t_linescan = None
            self.Update()
        else:
            # Calculate t_bin through number of bins per line and cycle time
            self.bins_per_line = self.BoxPrebin[8].GetValue()
            t_bin = 1.0 * self.t_linescan / self.bins_per_line
        # First we need to reset the linetime correction to zero
        self.linespin.SetValue(0)
        # Calculate binned data
        self.intData = self.Bin_Photon_Events(n_events=n_events, t_bin=t_bin)

        # Add to cache
        self.AddToCache(self.intData, self.filename)

        # Then Plot the data somehow
        self.Update()
        self.PlotImage()

    def OnBinning_Total(self, event=None):
        if self.BoxPrebin[6].GetValue() == False:
            # from µs to system clock ticks
            t_bin = self.BoxPrebin[4].GetValue() * self.system_clock
            # If, reset previously achieved things
            self.t_linescan = None
            self.Update()
        else:
            # Calculate t_bin through number of bins per line and cycle time
            self.bins_per_line = self.BoxPrebin[8].GetValue()
            t_bin = 1.0 * self.t_linescan / self.bins_per_line
        self.t_bin = t_bin
        # First we need to reset the linetime correction to zero
        self.linespin.SetValue(0)
        # Calculate binned data
        self.intData = self.Bin_All_Photon_Events(self.datData)

        # Add to cache
        self.AddToCache(self.intData, self.filename)

        # Then Plot the data somehow
        self.PlotImage()

    def OnFindLineScanTime(self, event):
        """
        Find the time that the confocal microscope uses to capture a line
        of data. This is done via FFT.
        """
        # Fourier Transform
        cnData = fft(self.intData)
        N = len(cnData)
        # We only need positive/negative frequencies
        amplitude = np.abs(cnData[0:N // 2] * np.conjugate(cnData[0:N // 2]))
        #n_bins = len(self.intData)

        # Calculate the correct frequencies
        rate = 1. / self.t_bin
        frequency = fftfreq(N)[0:N // 2] * rate

        if self.BoxLineScan[1].GetValue() == True:
            # Find it automagically
            # The first big maximum is usually the second maximum
            idx = np.argmax(amplitude[10:]) + 10
            # The first maximum is what we want ERROR
            idx2 = np.argmax(amplitude[10:idx - 30]) + 10
            # Sometimes the first one was ok.
            if 0.1 * amplitude[idx] > amplitude[idx2]:
                idx2 = idx
            # We now have the maximum, but we actually want to have some
            # kind of a weighted maximum. For that we take k data points next
            # to the maximum and weigth them with their relative amplitude.
            k = 10
            timeweights = list()
            timeweights.append(1 / frequency[idx2])
            Pie = 1
            for i in np.arange(k):
                weighta = amplitude[idx2 + i + 1] / amplitude[idx2]
                weightb = amplitude[idx2 - i - 1] / amplitude[idx2]
                timeweights.append(weighta / frequency[idx2 + i + 1])
                timeweights.append(weightb / frequency[idx2 - i - 1])
                Pie = Pie + weighta + weightb

            timeweights = np.array(timeweights)
            ltime = np.sum(timeweights, dtype="float") / Pie
            self.t_linescan = ltime
            # Plot the results (not anymore, we do a low_prebin)
            # self.PlotImage()
            # Set Checkbox value to True: "use cycle time"
            self.BoxPrebin[6].SetValue(True)
            self.Update()
            self.OnBinning_Prebin()
        else:
            # Pop up a dialog with the fourier transform of the function
            # (log -plot) and let user decide which maximum to use.
            dlg = FFTmaxDialog(self, frequency, amplitude)
            dlg.Show()

    def OnLinetimeSelected(self, e=None):
        Dropdown = self.BoxInfo[2]
        Text = Dropdown.GetValue()
        test = Text.split(".", 1)
        for item in test:
            if not item.isdigit():
                return
        Value = np.float(Text)
        #sel = Dropdown.GetSelection()
        elements = list()
        for factor in [0.25, 0.5, 1.0, 2.0, 4]:
            elements.append(str(np.float(Value * factor)))
        Dropdown.SetItems(elements)
        Dropdown.SetSelection(2)
        # self.dropdown.SetSelection(0)
        # Translate selected time to clockticks
        # Value = self.t_linescan*1e-3/self.system_clock
        if self.system_clock is None:
            sysclck = 60
        else:
            sysclck = self.system_clock
        # Avoid making str to float conversion errors?
        # Use the second element, which is in the middle. (!!)
        self.t_linescan = np.float(elements[2]) * 1e3 * sysclck
        self.BoxPrebin[6].Enable()
        # self.Update()

    def OnMenuAbout(self, event):
        # Show About Information
        description = doc.description()
        licence = doc.licence()
        info = wx.adv.AboutDialogInfo()
        #info.SetIcon(wx.Icon('hunter.png', wx.BITMAP_TYPE_PNG))
        info.SetName('PyScanFCS')
        info.SetVersion(self.version)
        info.SetDescription(description)
        info.SetCopyright(u'(C) 2012 Paul Müller')
        info.SetWebSite('http://pyscanfcs.craban.de')
        info.SetLicence(licence)
        info.AddDeveloper(u'Paul Müller')
        info.AddDocWriter(u'Paul Müller')
        wx.adv.AboutBox(info)

    def OnMenuDocumentation(self, e=None):
        """ Get the documentation and view it with browser"""
        filename = doc.GetLocationOfDocumentation()
        if filename is None:
            # Now we have to tell the user that there is no documentation
            self.StatusBar.SetStatusText("...documentation not found.")
        else:
            self.StatusBar.SetStatusText("...documentation: " + filename)
            if platform.system().lower() == 'windows':
                os.system("start /b " + filename)
            elif platform.system().lower() == 'linux':
                os.system("xdg-open " + filename + " &")
            elif platform.system().lower() == 'darwin':
                os.system("open " + filename + " &")
            else:
                # defaults to linux style:
                os.system("xdg-open " + filename + " &")

    def OnMenuExit(self, e):
        # Exit the Program
        self.Close(True)  # Close the frame.

    def OnMenuSoftware(self, event):
        # Show About Information
        text = doc.SoftwareUsed()
        wx.MessageBox(text, 'Software', wx.OK | wx.ICON_INFORMATION)

    def OnMenuSupport(self, event):
        # Show About Information
        text = doc.support
        wx.MessageBox(text, 'Support', wx.OK | wx.ICON_INFORMATION)

    def OnMenuTest(self, e=None):
        misc.ArtificialDataDlg(self)

    def OnMenuWiki(self, e=None):
        """ Go to the GitHub Wiki page"""
        webbrowser.open(doc.GitWiki)

    def OnMultipleTau(self, e=None):
        """ Perform a multiple tau algorithm.
            We sneak in a plt.plot here and there
            so the user can take a look at the results.
        """
        # Reset the bleaching profile
        self.file_bleach_profile = list()
        wx.BeginBusyCursor()
        # Dirty, but makes it shorter. We need the namespace:

        def SaveAC(Gtype, traceData):
            for i in np.arange(num_traces):
                usedTrace = traceData[i * NM:(i + 1) * NM]
                # Get the tail for the last trace
                if i == num_traces - 1:
                    usedTrace = traceData[i * NM:]
                # Calculate AC function and trace with human readable length
                G = multipletau.autocorrelate(usedTrace,
                                              m=m, deltat=bintime, normalize=True)
                if self.MenuVerbose.IsChecked():
                    plt.figure(0)
                    plt.plot(G[:, 0], G[:, 1], "-")
                # Correction that finds the correct countrate
                # self.TraceCorrectionFactor is 1.0, if the user
                # did not check the "countrate filter"
                usedTrace = usedTrace * self.TraceCorrectionFactor
                trace = util.reduce_trace(usedTrace, bintime, length=700)
                # Save Correlation function
                csvfile = filenamedummy + "_" + \
                    Gtype + "_" + str(i + 1) + ".csv"
                self.SaveCSVFile(G, trace, csvfile, i + 1,
                                 num_traces, Type=Gtype)
                Arc.write(csvfile)
                os.remove(csvfile)

        def SaveCC(Gtype, tracea, traceb, swaptraces):
            for i in np.arange(num_traces):
                usedTa = tracea[i * NM:(i + 1) * NM]
                usedTb = traceb[i * NM:(i + 1) * NM]
                # Get the tail for the last trace
                if i == num_traces - 1:
                    usedTa = tracea[i * NM:]
                    usedTb = traceb[i * NM:]
                G = multipletau.correlate(usedTa, usedTb,
                                          m=m, deltat=bintime, normalize=True)
                if self.MenuVerbose.IsChecked():
                    plt.figure(0)
                    plt.plot(G[:, 0], G[:, 1], "--")
                # Correction that finds the correct countrate
                # self.TraceCorrectionFactor is 1.0, if the user
                # did not check the "countrate filter"
                usedTa = usedTa * self.TraceCorrectionFactor
                usedTb = usedTb * self.TraceCorrectionFactor
                tra = util.reduce_trace(usedTa, bintime, length=700)
                trb = util.reduce_trace(usedTb, bintime, length=700)
                # In order to keep trace1 trace1 and trace2 trace2, we
                # need to swap here:
                if swaptraces == True:
                    tra, trb = trb, tra
                # Save Correlation function
                csvfile = filenamedummy + "_" + \
                    Gtype + "_" + str(i + 1) + ".csv"
                self.SaveCSVFile(G, tra, csvfile, i + 1, num_traces,
                                 Type=Gtype, secondtrace=trb)
                Arc.write(csvfile)
                os.remove(csvfile)

        # Get some needed data
        # bin time in s (for the correlation function)
        bintime = self.t_linescan / self.system_clock / 1e6
        # m value for multiple tau algorithm
        m = self.Spinm.GetValue()
        # Number of traces to slice the big trace into
        num_traces = self.Spinslice.GetValue()
        # Number of bins next to the maximum to use for the trace
        num_next_max = self.Spinnumax.GetValue()
        # Whether full traces should be saved in separate files
        save_trace = self.CheckBoxSaveTrace.GetValue()

        # Define zip file name
        # filenamedummy is a non-wildcard filename
        wildcards = ["A.dat", ".dat", "A.fits", ".fits"]
        filenamedummy = self.filename
        for card in wildcards:
            lwc = len(card)
            if self.filename[-lwc:] == card:
                filenamedummy = self.filename[:-lwc]
        zipfilename = os.path.join(self.dirname, filenamedummy) + ".zip"

        OURMODE = self.ModeDropDown.GetSelection()
        # 0: 1 colour 1 focus   A
        # 1: 2 colours 1 focus  A+B
        # 2: 1 colour 1 foci    A
        # 3: Quad               A+B
        # 4: Pie                A+B

        if OURMODE != 0 and OURMODE != 2:
            # Bin the second file or check for a .fits file
            if self.filename[-6:] == "A.fits":
                # Open fits file and load second intData
                filename = self.filename[:-6] + "B.fits"
                fits = pyfits.open(os.path.join(self.dirname, filename))
                series = fits[0]
                intData2 = series.data
                # Set proper 1D shape for intdata
                length = self.intData2.shape[0] * self.intData2.shape[1]
                intData2.shape = length
            elif self.filename[-5:] == "A.dat":
                # Check if we have B.dat in the cache
                #
                # Open B.dat file
                filename = self.filename[:-5] + "B.dat"
                try:
                    bcache = self.cache[filename]
                    if (bcache["dirname"] != self.dirname or
                        bcache["bins_per_line"] != self.bins_per_line or
                            bcache["linetime"] != self.t_linescan):
                        # We are in the wrong directory
                        raise KeyError
                except KeyError:
                    # Open B.dat and add to cache
                    path = os.path.join(self.dirname, filename)

                    wxdlg = uilayer.wxdlg(parent=self, steps=3,
                                          title="Importing dat file...")
                    datData2 = openfile.openDAT(
                        path, callback=wxdlg.Iterate)["data_stream"]
                    wxdlg.Finalize()

                    # Bin to obtain intData2
                    intData2 = self.Bin_All_Photon_Events(datData2)
                    # Add to cache
                    self.AddToCache(intData2, filename, background=True)
                else:
                    intData2 = 1 * bcache["data"]

            else:
                # We should not be here.
                print("No A.dat or A.fits file opened. Aborting.")
                return

        # Start plotting?
        if self.MenuVerbose.IsChecked():
            plt.figure(0)
            plt.subplot(111)

        # Create .zip archive
        Arc = zipfile.ZipFile(zipfilename, mode='w')
        returnWD = os.getcwd()
        tempdir = tempfile.mkdtemp()
        os.chdir(tempdir)

        # 1 color 1 focus
        if self.ModeDropDown.GetSelection() == 0:
            traceData = self.GetTraceFromIntData(
                self.intData, self.XY_Trace_square)
            # Variable *SaveAC* will need.
            NM = int(np.floor(len(traceData) / num_traces))
            traces = [traceData]
            # Get autocorrelation functions of splitted trace
            Gtype = "AC_A1"
            SaveAC(Gtype, traceData)

        # 2 colour 1 focus
        elif self.ModeDropDown.GetSelection() == 1:
            traceData1 = self.GetTraceFromIntData(self.intData,
                                                  self.XY_Trace_square, title="Region A1")
            NM = int(np.floor(len(traceData1) / num_traces))
            traceData2 = self.GetTraceFromIntData(intData2,
                                                  self.XY_Trace_square, title="Region B1")
            # Get autocorrelation functions of splitted trace
            traces = [traceData1, traceData2]
            # Save Autocorrelation
            for j in np.arange(len(traces)):
                traceData = traces[j]
                if j == 0:
                    Gtype = "AC_A1"
                else:  # j==1
                    Gtype = "AC_B1"
                SaveAC(Gtype, traceData)
            # Save Cross correlation
            for j in np.arange(len(traces)):
                if j == 0:
                    Gtype = "CC_A1B1"
                    tracea = traces[0]
                    traceb = traces[1]
                    swaptraces = False
                else:  # j==1
                    Gtype = "CC_B1A1"
                    tracea = traces[1]
                    traceb = traces[0]
                    swaptraces = True
                SaveCC(Gtype, tracea, traceb, swaptraces)

        # 1 Colour 2 Foci
        elif self.ModeDropDown.GetSelection() == 2:
            traceData1 = self.GetTraceFromIntData(self.intData,
                                                  self.XY_Trace_square, title="Region A1")
            NM = int(np.floor(len(traceData1) / num_traces))
            traceData2 = self.GetTraceFromIntData(self.intData,
                                                  self.XY_Trace_squareB, title="Region A2")
            # Get autocorrelation functions of splitted trace
            traces = [traceData1, traceData2]
            # Save Autocorrelation
            for j in np.arange(len(traces)):
                traceData = traces[j]
                if j == 0:
                    Gtype = "AC_A1"
                else:  # j==1
                    Gtype = "AC_A2"
                SaveAC(Gtype, traceData)

            # Save Cross correlation
            for j in np.arange(len(traces)):
                if j == 0:
                    Gtype = "CC_A1A2"
                    tracea = traces[0]
                    traceb = traces[1]
                    swaptraces = False
                else:  # j==1
                    Gtype = "CC_A2A1"
                    tracea = traces[1]
                    traceb = traces[0]
                    swaptraces = True
                SaveCC(Gtype, tracea, traceb, swaptraces)

        # Quad
        elif self.ModeDropDown.GetSelection() == 3:
            traceData1 = self.GetTraceFromIntData(self.intData,
                                                  self.XY_Trace_square, title="Region A1")
            NM = int(np.floor(len(traceData1) / num_traces))
            traceData2 = self.GetTraceFromIntData(self.intData,
                                                  self.XY_Trace_squareB, title="Region A2")
            traceData3 = self.GetTraceFromIntData(intData2,
                                                  self.XY_Trace_square, title="Region B1")
            traceData4 = self.GetTraceFromIntData(intData2,
                                                  self.XY_Trace_squareB, title="Region B2")
            # Get autocorrelation functions of splitted trace
            traces = [traceData1, traceData2, traceData3, traceData4]
            Gtypes = ["AC_A1", "AC_A2", "AC_B1", "AC_B2"]
            # Save Autocorrelation
            for j in np.arange(len(traces)):
                traceData = traces[j]
                Gtype = Gtypes[j]
                SaveAC(Gtype, traceData)

            # Save Cross correlation
            Gtypes = ["A1", "A2", "B1", "B2"]
            for j in np.arange(4):
                for k in np.arange(4):
                    if j != k:
                        Gtype = "CC_" + Gtypes[j] + Gtypes[k]
                        tracea = traces[j]
                        traceb = traces[k]
                        if j < k:
                            swaptraces = False
                        else:
                            swaptraces = True
                        SaveCC(Gtype, tracea, traceb, swaptraces)

        # PIE
        elif self.ModeDropDown.GetSelection() == 4:
            traceData1 = self.GetTraceFromIntData(self.intData,
                                                  self.XY_Trace_square, title="Region A1")
            NM = int(np.floor(len(traceData1) / num_traces))
            traceData2 = self.GetTraceFromIntData(intData2,
                                                  self.XY_Trace_squareB, title="Region B2")
            # Get autocorrelation functions of splitted trace
            traces = [traceData1, traceData2]
            # Save Autocorrelation
            for j in np.arange(len(traces)):
                traceData = traces[j]
                if j == 0:
                    Gtype = "AC_A1"
                else:  # j==1
                    Gtype = "AC_B2"
                SaveAC(Gtype, traceData)

            # Save Cross correlation
            for j in np.arange(len(traces)):
                if j == 0:
                    Gtype = "CC_A1B2"
                    tracea = traces[0]
                    traceb = traces[1]
                    swaptraces = False
                else:  # j==1
                    Gtype = "CC_B2A1"
                    tracea = traces[1]
                    traceb = traces[0]
                    swaptraces = True
                SaveCC(Gtype, tracea, traceb, swaptraces)

        # Add bleaching profile files

        for bleach_file in self.file_bleach_profile:
            olddir = os.getcwd()
            os.chdir(os.path.dirname(bleach_file))
            try:
                Arc.write(os.path.basename(bleach_file))
            except:
                pass
            os.chdir(olddir)

            Arc.close()
        os.chdir(returnWD)
        try:
            os.removedirs(tempdir)
        except:
            pass

        if self.MenuVerbose.IsChecked():
            plt.figure(0)
            plt.semilogx()
            plt.ylabel('Correlation')
            plt.xlabel('Lag time [s]')
            plt.show()

        # Save all the traces
        if save_trace == True:
            for i in np.arange(len(traces)):
                filename = filenamedummy + "_" + str(i) + ".txt"
                filename = os.path.join(self.dirname, filename)
                openedfile = open(filename, 'wb')
                openedfile.write('# This file was created using PyScanFCS v.' +
                                 self.version + "\r\n")
                openedfile.write("# Source file: " + filenamedummy + "\r\n")
                openedfile.write("# linetime [s]: " + str(bintime) + "\r\n")
                openedfile.write("# bins per line: " +
                                 str(self.bins_per_line) + "\r\n")
                openedfile.write("# bins used per line: " +
                                 str(2 * num_next_max + 1) + "\r\n")
                for j in np.arange(len(traces[i])):
                    openedfile.write(str(traces[i][j]) + "\r\n")

        wx.EndBusyCursor()

    def OnOpenBinned(self, e):
        # Open a data file
        """Import experimental data from a file."""
        dlg = wx.FileDialog(self, "Choose a binned data file", self.dirname, "",
                            openfile.wx_dlg_wc_binned, wx.FD_OPEN)
        # user cannot do anything until he clicks "OK"
        if dlg.ShowModal() == wx.ID_OK:

            # Workaround for Ubuntu 12.10 since 0.2.0
            (self.dirname, self.filename) = os.path.split(dlg.GetPath())
            #self.filename = dlg.GetFilename()
            #self.dirname = dlg.GetDirectory()

            info = openfile.openAny(os.path.join(self.dirname, self.filename))

            print(info)

            self.imgData = None
            self.intData = info["data_binned"]
            self.datData = None

            # Set all variables
            self.system_clock = info['system_clock']
            self.T_total = info["total_time"]
            self.t_linescan = info["line_time"]
            self.t_bin = info["bin_time"]

            if info["bin_shift"] is not None:
                self.BoxPrebin[10].SetValue(info["bin_shift"])

            self.bins_per_line = info["bins_per_line"]
            self.prebpl.SetValue(self.bins_per_line)

            # Plot
            # Set proper 1D shape for intdata
            length = info["size"]
            self.intData.shape = length
            self.Update()
            self.PlotImage()

    # Current
    def OnOpenStream(self, e):
        # Open a data file
        """
        We open a .dat file as produced by the "Flex02-12D" correlator in photon
        history recorder mode.
        The file contains the time differences between single photon events.

        Returns:
        This function makes the filename publicly available, bins a couple
        of events to get 1e+6 points and plots them into the plotting area
        (self.plotarea), using the Bin_Photon_Events() function.

        Raw data file format (taken from manual):
         1. The file records the difference in system clock ticks (1/60 us)
            between photon event.
         2. The first byte identifies the format of the file 8 : 8 bit, 16: 16 bit
         3. The second byte identifies the system clock. 60MHz.
         4. The time unit is 1/system clock.
         5. 16 bit format. Each WORD (2 bytes) represents a photon event, 
            time = WORD/system clock, unless the value is 0xFFFF, in which case, 
            the following four bytes represent a photon event.
         6. 8 bit format: Each BYTE represents a photon event unless the value is 
            0xFF, in which case, the BYTE means 255 clock ticks passed without a 
            photon event. For example 0A 0B FF 08 means there are three
            photon events. The time series are 0x0A+1, 0x0B+1, 0xFF+8+1.

        """
        # File Dialog
        dlg = wx.FileDialog(self, "Choose a photon stream file", self.dirname, "",
                            openfile.wx_dlg_wc_stream, wx.FD_OPEN)
        # user cannot do anything until he clicks "OK"
        if dlg.ShowModal() == wx.ID_OK:
            # Workaround for Ubuntu 12.10 since 0.2.0
            (self.dirname, self.filename) = os.path.split(dlg.GetPath())
            #self.filename = dlg.GetFilename()
            #self.dirname = dlg.GetDirectory()
            filename = os.path.join(self.dirname, self.filename)

            wxdlg = uilayer.wxdlg(parent=self, steps=3,
                                  title="Importing photon stream...")
            info = openfile.openAny(filename, callback=wxdlg.Iterate)
            self.system_clock = info["system_clock"]
            self.datData = info["data_stream"]

            wxdlg.Finalize()
            self.GetTotalTime()
            self.Update()

    def OnRadioSelector(self, e=None):
        # Define what style of selector will be used in plot.
        if self.RbtnLinet.Value == True:
            self.plotarea.UseLineSelector()
        else:
            self.plotarea.UseRectangleSelector()
        self.Update()

    def OnSaveFits(self, e):
        # Save the Data
        """ Save binned data as a 2d array (image) """
        if self.filename[-4:] == ".dat":
            newfilename = self.filename[:-4] + ".fits"
        else:
            newfilename = ""
        dlg = wx.FileDialog(self, "Choose a data file", self.dirname, newfilename,
                            "FITS files (*.fits)|*.Fits;*.FITS;*.fits",
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        # user cannot do anything until he clicks "OK"
        if dlg.ShowModal() == wx.ID_OK:
            # Workaround for Ubuntu 12.10 since 0.2.0
            (self.dirname, newfilename) = os.path.split(dlg.GetPath())
            #newfilename = dlg.GetFilename()
            #self.dirname = dlg.GetDirectory()
            # Creating image array
            M = len(self.intData)
            Ny = self.bins_per_line
            Nx = int(M / Ny) + 1
            # Plotting data will have some zeros at the end
            plotdata = np.zeros(Nx * Ny)
            # Check for maximum in self.intData
            maxint = np.max(self.intData)
            if maxint < 256:
                plotdata = np.uint8(plotdata)
                plotdata[0:M] = np.uint8(self.intData)
            else:
                plotdata[0:M] = self.intData
            plotdata.shape = (Nx, Ny)
            hdu = pyfits.PrimaryHDU(plotdata)
            hdulist = pyfits.HDUList([hdu])
            header = hdulist[0].header
            # Add some constants:
            cards = []
            cards.append(pyfits.Card('SysClck', self.system_clock,
                                     "System clock [MHz]"))
            if self.T_total is not None:
                cards.append(pyfits.Card('Total', self.T_total,
                                         "Total time in system clock ticks"))
            if self.t_linescan is not None:
                t_linescan = self.t_linescan
            else:
                t_linescan = self.t_bin * len(self.imgData)

            cards.append(pyfits.Card('Tcycle', t_linescan,
                                     "Time for each linescan in system clock ticks"))
            cards.append(pyfits.Card('Tbin', self.t_bin,
                                     "Time for each bin in system clock ticks"))
            eb = self.BoxPrebin[10].GetValue()
            cards.append(pyfits.Card('Binshift', eb,
                                     "Empty bins before actual binning of data"))

            for c in cards:
                c.verify()
                header.update(c.key, c.value, c.comment)
            # clobber=True: Overwrites file.
            hdulist.writeto(os.path.join(
                self.dirname, newfilename), clobber=True)

    def OnSaveDat(self, e):
        # Save the Data
        """
        Save experimental data as 32bit format.

        Raw data file format:
         1. The file records the difference in system clock ticks (1/60 us)
            between photon events.
         2. The first byte identifies the format of the file: 32 bit
         3. The second byte identifies the system clock: usually 60MHz.
         4. The time unit is 1/system clock.
         5. 32 bit format. 4 bytes represent a photon event, 
            time = 4 bytes/system clock
        """
        # Make a reasonable 32bit filename
        if self.filename[-5:] == "A.dat":
            newfilename = self.filename[:-5] + "_32bit_A.dat"
        elif self.filename[-5:] == "B.dat":
            newfilename = self.filename[:-5] + "_32bit_B.dat"
        else:
            newfilename = self.filename[:-4] + "_32bit.dat"
        dlg = wx.FileDialog(self, "Choose a data file", self.dirname, newfilename,
                            "DAT files (*.dat)|*.dat;*.daT;*.dAt;*.dAT;*.Dat;*.DaT;*.DAt;*.DAT",
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        # user cannot do anything until he clicks "OK"
        if dlg.ShowModal() == wx.ID_OK:
            # Workaround for Ubuntu 12.10 since 0.2.0
            (self.dirname, newfilename) = os.path.split(dlg.GetPath())
            #newfilename = dlg.GetFilename()
            #self.dirname = dlg.GetDirectory()
            NewFile = open(os.path.join(self.dirname, newfilename), 'wb')
            newformat = np.uint8(32)
            newclock = np.uint8(self.system_clock)
            NewFile.write(newformat)
            NewFile.write(newclock)
            self.datData.tofile(NewFile)
            NewFile.close()

    def OnSelectPlot(self, eclick, erelease):
        # Define what will happen upon clicking on the plot.
        if self.RbtnLinet.Value == True:
            self.OnSelectLineTime(eclick, erelease)
        else:
            self.OnSelectRegion(eclick, erelease)
        self.Update()

    def OnSelectCache(self, e=None):
        for item in self.cachemenu.GetMenuItems():
            if item.IsChecked():
                cachename = item.GetLabel()
        cache = self.cache[cachename]
        self.BoxPrebin[8].SetValue(cache["bins_per_line"])
        self.bins_per_line = cache["bins_per_line"]
        linetime = cache["linetime"]
        if linetime is not None:
            self.BoxInfo[2].SetValue(str(linetime / self.system_clock / 1e3))
        self.t_linescan = linetime
        self.intData = 1 * cache["data"]
        self.filename = cachename
        self.dirname = cache["dirname"]
        filename = os.path.join(self.dirname, self.filename)

        wxdlg = uilayer.wxdlg(parent=self, steps=3,
                              title="Importing dat file...")
        info = openfile.openDAT(filename, callback=wxdlg.Iterate)
        self.system_clock = info["system_clock"]
        self.datData = info["data_stream"]
        wxdlg.Finalize()

        self.GetTotalTime()
        self.Update()
        self.PlotImage()

    def OnSelectLineTime(self, eclick, erelease):

        y1 = eclick.ydata
        y2 = erelease.ydata
        Tx1 = eclick.xdata
        Tx2 = erelease.xdata

        if Tx1 == Tx2:
            return

        # Since x and y ahve different scales, we need to
        # multiply the y-part with 1e3 to get ms instead of s.
        #
        # See in PlotImage below:
        #Tx = self.t_bin*Nx/self.system_clock/1e3
        #Ty = Tx*Ny/1e3
        #
        x1 = 1e3 * Tx1
        x2 = 1e3 * Tx2

        if x1 > x2:
            y2, y1 = y1, y2
            x1, x2 = x2, x1

        # Calculate correction factor
        delta = (y2 - y1) / (x2 - x1)
        # Calculate how much percent that is
        percent = delta * 100.

        self.linespin.SetValue(np.float(percent))
        self.percent = percent
        self.CorrectLineTime(event=None)

    def OnSelectRegion(self, eclick=None, erelease=None, fullMT=False):
        """ Internally sets the region in the kymograph

            `eclick` and `erelease` are matplotlib events on a plot

            if `fulMT` is True and `eclick` and `erelease` are None,
            then the x-values are overridden and old y-values are used.
        """

        if eclick is None and erelease is None and fullMT is True:
            # try to get data from two sources:
            if self.RbtnSelect.Value == True:
                try:
                    (y1, y2) = self.XY_Trace_square[1]
                    # Line_time [ms] - convert to ms from (us and clock ticks)
                    y1 /= 1e3 * self.system_clock
                    y2 /= 1e3 * self.system_clock
                except:
                    pass
            else:
                try:
                    (y1, y2) = self.XY_Trace_squareB[1]
                    # Line_time [ms] - convert to ms from (us and clock ticks)
                    y1 /= 1e3 * self.system_clock
                    y2 /= 1e3 * self.system_clock
                except:
                    pass
            if (y1, y2) == (None, None):
                (y1, y2) = self.plotarea.axes.get_ylim()
            # Get absolute x values
            (x1, x2) = self.plotarea.axes.get_xlim()
        else:
            x1 = eclick.xdata
            x2 = erelease.xdata
            y1 = eclick.ydata
            y2 = erelease.ydata

        # Sort values
        if x1 > x2:
            x1, x2 = x2, x1
        elif x1 == x2:
            x2 = x1 + 1
        if y1 > y2:
            y1, y2 = y2, y1
        elif y1 == y2:
            y2 = y1 + 1

        # Set the values of the corresponding spin controls
        # To Do

        # We have to distinguish between yellow and cyan square.
        # self.square: yellow square
        # self.square2: cyan square
        if self.RbtnSelect.Value == True:
            square = self.square
            oldsquare = self.squareB
            square_color = "yellow"
            oldsquare_color = "cyan"
            oldcoords = self.XY_Trace_squareB
        else:
            square = self.squareB
            oldsquare = self.square
            square_color = "cyan"
            oldsquare_color = "yellow"
            oldcoords = self.XY_Trace_square

        # We should also plot it
        if square is not None:
            # Remove the old same coloured square
            square.remove()
        square = Rectangle((x1, y1), abs(x2 - x1), abs(y2 - y1),
                           alpha=0.1, color=square_color)
        self.plotarea.axes.add_patch(square)

        # Adjust the old square:
        if oldsquare is not None:
            oldsquare.remove()
            oldsquare = None
        if oldcoords[1] == (None, None):
            (yn1, yn2) = (y1, y2)
        else:
            (yn1, yn2) = oldcoords[1]
            yn1 *= 1e-3 / self.system_clock
            yn2 *= 1e-3 / self.system_clock

        if self.ModeDropDown.GetSelection() > 1:

            oldsquare = Rectangle((x1, yn1), abs(x2 - x1), abs(yn2 - yn1),
                                  alpha=0.1, color=oldsquare_color)
            self.plotarea.axes.add_patch(oldsquare)

        self.plotarea.canvas.draw()

        # Convert values to array indices and make public.
        # Total_time [s] (convert to us and then to clock ticks)
        x1 = (x1 * 1e6 * self.system_clock)
        x2 = (x2 * 1e6 * self.system_clock)
        # Line_time [ms] (convert to us and then to clock ticks)
        y1 = (y1 * 1e3 * self.system_clock)
        y2 = (y2 * 1e3 * self.system_clock)

        if self.RbtnSelect.Value == True:
            self.square = square
            self.XY_Trace_square = [(x1, x2), (y1, y2)]
            self.squareB = oldsquare
            if oldsquare is not None:
                self.XY_Trace_squareB[0] = (x1, x2)

        else:
            self.squareB = square
            self.XY_Trace_squareB = [(x1, x2), (y1, y2)]
            self.square = oldsquare
            if oldsquare is not None:
                self.XY_Trace_square[0] = (x1, x2)

    def OnSetFullMeasTime(self, e=None):
        """ Sets the full range of the measurement time
        """
        self.OnSelectRegion(fullMT=True)

    def PlotImage(self):
        """
            Plot self.intData. If not enough information about
            e.g. cycle time is given we have to guess the dimensions
            of the plot.
        """
        M = len(self.intData)
        self.bins_per_line = Ny = self.BoxPrebin[8].GetValue()
        Nx = int(np.floor(M / Ny))
        # This checkbox is False, if we do not want to use t_linescan
        # to set the length of a line.
        if self.BoxPrebin[6].GetValue() == False:
            # from µs to system clock ticks
            self.t_bin = self.BoxPrebin[4].GetValue() * self.system_clock
        else:
            self.t_bin = self.t_linescan / self.bins_per_line
        # This is a fast way of slicing our 1D intData array to a shorter
        # plottable 2D array.
        if Nx > Ny:
            # Number of lines we have to jump over
            P = Nx // Ny
            Nx = P * Ny
            plotdata = np.zeros((Ny, Ny))
            MAX = Nx * Ny

            for abin in np.arange(Ny):
                # Take every P'th element in Nx direction
                plotdata[abin] = self.intData[abin:MAX + abin:Ny * P]
        else:
            # We are lucky
            plotdata = self.intData[:Nx * Ny]
            plotdata.shape = (Nx, Ny)
            plotdata = plotdata.transpose()

        self.plotarea.image.set_data(plotdata)
        # Set labels y [ms] and x [s]
        Ty = self.t_bin * Ny / 1e3 / self.system_clock

        # try line time for x-scale first
        if self.t_linescan is not None:
            Tx = Nx * self.t_linescan * 1e-6 / self.system_clock
        else:
            Tx = Ty * Nx / 1e3

        self.plotarea.image.set_extent((0, Tx, Ty, 0))
        # Make the square or else we would not see much
        self.plotarea.axes.set_aspect(1. * Tx / Ty)

        vmin = np.min(plotdata)
        vmax = np.max(plotdata)
        self.plotarea.colorbar.set_clim(vmin, vmax)
        self.plotarea.colorbar.vmin = vmin
        self.plotarea.colorbar.vmax = vmax
        self.plotarea.colorbar.update_normal(self.plotarea.image)
        self.plotarea.colorbar.set_ticks(
            np.arange(vmax + 1), update_ticks=True)
        self.plotarea.canvas.draw()

        self.imgData = plotdata

    def SaveCSVFile(self, G, trace, csvfile, num=1, num_traces=1, Type="AC",
                    secondtrace=None):

        with open(csvfile, 'w') as fd:
            fd.write('# This file was created using PyScanFCS v.' +
                             self.version + "\r\n")
            fd.write("# Source file \t" + self.filename + "\r\n")
            fd.write("# Source slice \t" + str(num) +
                             " of " + str(num_traces) + "\r\n")
            fd.write('# Channel (tau [s]) \t Correlation function \r\n')
            if Type[:2] == "CC":
                fd.write(
                    "# Type AC/CC \t Cross-Correlation " + Type[2:] + "\r\n")
            else:
                fd.write(
                    "# Type AC/CC \t Autocorrelation " + Type[2:] + "\r\n")
            dataWriter = csv.writer(fd, delimiter='\t')
            for i in np.arange(len(G)):
                dataWriter.writerow([str(G[i, 0]) + " \t", str(G[i, 1])])
            fd.write('# BEGIN TRACE \r\n')
            fd.write('# Time ([s]) \t Intensity Trace [kHz] \r\n')
            for i in np.arange(len(trace)):
                dataWriter.writerow(
                    [str("%.10e") % trace[i, 0], str("%.10e") % trace[i, 1]])
    
            if secondtrace is not None:
                fd.write('#\r\n# BEGIN SECOND TRACE \r\n')
                fd.write('# Time ([s]) \t Intensity Trace [kHz] \r\n')
                for i in np.arange(len(trace)):
                    dataWriter.writerow([str("%.10e") % secondtrace[i, 0],
                                         str("%.10e") % secondtrace[i, 1]])

    def Update(self, e=None):
        self.UpdateInfo()
        # Box Prebin
        # self.BoxPrebin.append(prebox)       # 0 box
        # self.BoxPrebin.append(pretext)      # 1 text: enter # events to use
        # self.BoxPrebin.append(prespin)      # 2 spin: how many bins to bin
        # self.BoxPrebin.append(pretextt)     # 3 text: enter bin width
        # self.BoxPrebin.append(prespint)     # 4 spin: bin time
        # self.BoxPrebin.append(prebutt)      # 5 button
        # self.BoxPrebin.append(precheck)     # 6 checkbox: use linetime
        # self.BoxPrebin.append(prebplt)      # 7 text: bins per line
        # self.BoxPrebin.append(self.prebpl)  # 8 spin: bins per line
        if self.datData is not None:
            self.menuSaveDat.Enable(True)
            for item in self.BoxPrebin:
                item.Enable()
            for item in self.BoxInfo:
                item.Enable()
            if self.t_linescan is not None:
                for item in self.BoxBinTotal:
                    item.Enable()
            else:
                for item in self.BoxBinTotal:
                    item.Disable()
        if self.t_linescan is not None:
            # This means a linetime has been found
            self.BoxPrebin[6].Enable()
            # self.BoxPrebin[6].SetValue(True)
        else:
            self.BoxPrebin[6].Disable()
            self.BoxPrebin[6].SetValue(False)
        checked = self.BoxPrebin[6].GetValue()
        if checked == True:
            self.BoxPrebin[3].Disable()
            self.BoxPrebin[4].Disable()
        else:
            self.BoxPrebin[3].Enable()
            self.BoxPrebin[4].Enable()
        # If no data is present, do not enable anything
        if self.datData is None:
            self.menuSaveDat.Enable(False)
            for item in self.BoxPrebin:
                item.Disable()
            for item in self.BoxBinTotal:
                item.Disable()
            for item in self.BoxInfo:
                item.Disable()

        # Box scan cycle time / Image Selection / Save Fits
        if self.intData is None:
            self.menuSaveFits.Enable(False)
            for item in self.BoxLineScan:
                item.Disable()
            for item in self.BoxImageSelection:
                item.Disable()
        else:
            self.menuSaveFits.Enable(True)
            for item in self.BoxLineScan:
                item.Enable()
            for item in self.BoxImageSelection:
                item.Enable()

        # Modes
        if self.ModeDropDown.GetSelection() > 1 and self.intData is not None:
            self.RbtnSelectB.Enable()
        else:
            self.RbtnSelectB.Disable()

        # MultipleTau Box
        if self.square is None:
            for item in self.BoxMultipleTau:
                item.Disable()
        else:
            for item in self.BoxMultipleTau:
                item.Enable()

    def UpdateInfo(self):
        # Initial data values:

        if self.system_clock is not None:
            self.BoxInfo[0].SetLabel(
                "System clock [MHz]: " + str(self.system_clock))
            if self.T_total is not None:
                # This means a file has been opened
                self.BoxInfo[1].SetLabel("Total time [s]: {:.5f}".format(
                    self.T_total * 1e-6 / self.system_clock))
        if self.t_linescan is not None:
            # This means a linetime has been found
            self.BoxInfo[2].SetValue(
                str(self.t_linescan * 1e-3 / self.system_clock))
            self.OnLinetimeSelected()


def MyExceptionHook(etype, value, trace):
    """
    Handler for all unhandled exceptions.

    :param `etype`: the exception type (`SyntaxError`, `ZeroDivisionError`, etc...);
    :type `etype`: `Exception`
    :param string `value`: the exception error message;
    :param string `trace`: the traceback header, if any (otherwise, it prints the
     standard Python header: ``Traceback (most recent call last)``.
    """
    wx.GetApp().GetTopWindow()
    tmp = traceback.format_exception(etype, value, trace)
    exception = "".join(tmp)

    dlg = ExceptionDialog(exception)
    dlg.ShowModal()
    dlg.Destroy()
    wx.EndBusyCursor()



# VERSION
version = doc.__version__
__version__ = version

print(doc.info(version))

# Start gui


def Main():
    app = wx.App(False)
    MyFrame(None, -1, version)
    app.MainLoop()


if __name__ == "__main__":
    Main()
