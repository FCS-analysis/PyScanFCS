"""Miscellaneous classes"""
import codecs
import os
import sys

import numpy as np
import wx
import wx.lib.delayedresult as delayedresult


# The icon file was created with
# img2py -i -n Main PyScanFCS_icon.png icon.py
from . import icon
from . import edclasses


class ArtificialDataDlg(wx.Frame):
    # This tool is derived from a wx.frame.
    def __init__(self, parent):
        self.parent = parent
        # Get the window positioning correctly
        pos = self.parent.GetPosition()
        pos = (pos[0] + 100, pos[1] + 100)
        wx.Frame.__init__(self, parent=self.parent,
                          title="Create artificial test data", pos=pos,
                          style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)

        # Content
        self.panel = wx.Panel(self)

        topSizer = wx.BoxSizer(wx.VERTICAL)

        topSizer.Add(wx.StaticText(self.panel,
                                   label="Create artificial test data\n" +
                                   "with exponentially correlated noise.\n"))

        colsizer = wx.FlexGridSizer(4, 2, 20)

        # decay time
        colsizer.Add(wx.StaticText(self.panel,
                                   label="Correlation time [ms]: "))
        self.WXDecay = edclasses.FloatSpin(self.panel, value="100")
        colsizer.Add(self.WXDecay)

        # line scanning time
        colsizer.Add(wx.StaticText(self.panel,
                                   label="Scan cycle time [ms]: "))
        self.WXLine = edclasses.FloatSpin(self.panel, value="0.714")
        colsizer.Add(self.WXLine)

        # number of samples
        colsizer.Add(wx.StaticText(self.panel,
                                   label="Number of samples: "))
        self.WXNumber = wx.SpinCtrl(self.panel, -1, min=10000,
                                    max=500000000, value="500000")
        colsizer.Add(self.WXNumber)

        # data format
        colsizer.Add(wx.StaticText(self.panel, label="Data format: "))
        self.WXDropInt = wx.ComboBox(self.panel, -1, "uint16", (15, 30),
                                     wx.DefaultSize, ["uint16", "uint32"],
                                     wx.CB_DROPDOWN | wx.CB_READONLY)
        colsizer.Add(self.WXDropInt)

        topSizer.Add(colsizer)

        btndo = wx.Button(self.panel, wx.ID_CLOSE, 'Create .dat file')
        # Binds the button to the function - close the tool

        self.Bind(wx.EVT_BUTTON, self.OnCreateFile, btndo)

        topSizer.Add(btndo)
        self.panel.SetSizer(topSizer)
        topSizer.Layout()
        topSizer.Fit(self)
        # self.SetMinSize(colsizer.GetMinSizeTuple())
        # Icon
        if parent.MainIcon is not None:
            wx.Frame.SetIcon(self, parent.MainIcon)
        self.Show(True)

    def OnClose(self, event=None):
        # This is a necessary function for PyCorrFit.
        # Do not change it.
        self.parent.toolmenu.Check(self.MyID, False)
        self.parent.ToolsOpen.__delitem__(self.MyID)
        self.Destroy()

    def OnCreateFile(self, e=None):
        linetime = self.WXLine.GetValue()
        taudiff = self.WXDecay.GetValue()
        N = self.WXNumber.GetValue()
        inttype = self.WXDropInt.GetValue()

        if inttype == "uint16":
            dtype = np.uint16
        else:
            dtype = np.uint32

        # file dialog
        filename = "test_tau{}ms_line{}ms_N{}_{}.dat".format(
            taudiff, linetime, N, inttype)

        dlg = wx.FileDialog(self, "Save as .dat file", "./", filename,
                            "DAT files (*.dat)|*.dat;*.daT;*.dAt;*.dAT;*.Dat;*.DaT;*.DAt;*.DAT",
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        # user cannot do anything until he clicks "OK"
        if dlg.ShowModal() == wx.ID_OK:
            # Workaround for Ubuntu 12.10 since 0.2.0
            path = dlg.GetPath()
        else:
            return

        wx.BeginBusyCursor()

        # start new thread
        args = N, taudiff, linetime, dtype, path
        delayedresult.startWorker(_CreateConsumer, _CreateWorker,
                                  wargs=(args,),)


def GenerateExpNoise(N, taud=20., variance=1., deltat=1.):
    """
        Generate exponentially correlated noise.
    """
    # length of mean0 trace
    N_steps = N
    dt = deltat
    # AR-1 processes - what does that mean?
    # time constant (inverse of correlationtime taud)
    g = 1. / taud
    # variance
    s0 = variance

    # normalization factor (memory of the trace)
    exp_g = np.exp(-g * dt)
    one_exp_g = 1 - exp_g
    z_norm_factor = np.sqrt(1 - np.exp(-2 * g * dt)) / one_exp_g

    # create random number array
    # generates random numbers in interval [0,1)
    randarray = np.random.random(N_steps)
    # make numbers random in interval [-1,1)
    randarray = 2 * (randarray - 0.5)

    # simulate exponential random behavior
    z = np.zeros(N_steps)
    z[0] = one_exp_g * randarray[0]
    for i in np.arange(N_steps - 1) + 1:
        z[i] = exp_g * z[i - 1] + one_exp_g * randarray[i]

    z = z * z_norm_factor * s0
    return z


def MakeDat(linetime, noisearray, dtype, filename):
    """ Create a .dat file (like Photon.exe).
        System clock is fixed to 60MHz.
        linetime [s]
        noisearray integer array (uint16 or uint32)
    """
    NewFile = open(filename, 'wb')
    if dtype == np.uint32:
        newformat = np.uint8(32)
    elif dtype == np.uint16:
        newformat = np.uint8(16)
    else:
        raise ValueError
    newclock = np.uint8(60)
    NewFile.write(newformat)
    NewFile.write(newclock)
    noisearray = dtype(noisearray)
    # Create matrix. Each line is a scan.
    timeticks = linetime * newclock * 1e6  # 60MHz
    half1 = np.ceil(timeticks / 2)
    half2 = np.floor(timeticks / 2)
    for i in np.arange(len(noisearray)):
        # Create a line
        N = noisearray[i]
        if N == 0:
            line = np.zeros(1, dtype=dtype)
            # Only one event at the far corner
            line[0] = timeticks
            line.tofile(NewFile)
        else:
            line = np.ones(N + 1, dtype=dtype)
            # events are included between two far events
            line[0] = half1 - len(line)
            line[-1] = half2
            line.tofile(NewFile)
    NewFile.close()


def removewrongUTF8(name):
    newname = u""
    for char in name:
        try:
            codecs.decode(char, "UTF-8")
        except:
            pass
        else:
            newname += char
    return newname


def getMainIcon(pxlength=32):
    """ *pxlength* is the side length in pixels of the icon """
    # Set window icon
    iconBMP = icon.getMainBitmap()
    # scale
    image = wx.Bitmap.ConvertToImage(iconBMP)
    image = image.Scale(pxlength, pxlength, wx.IMAGE_QUALITY_HIGH)
    iconBMP = wx.Bitmap(image)
    iconICO = wx.Icon(iconBMP)
    return iconICO


def findprogram(program):
    """ Uses the systems PATH variable find executables"""
    path = os.environ['PATH']
    paths = path.split(os.pathsep)
    for d in paths:
        if os.path.isdir(d):
            fullpath = os.path.join(d, program)
            if sys.platform[:3] == 'win':
                for ext in '.exe', '.bat':
                    program_path = fullpath + ext
                    if os.path.isfile(fullpath + ext):
                        return (1, program_path)
            else:
                if os.path.isfile(fullpath):
                    return (1, fullpath)
    return (0, None)


def _CreateConsumer(e=None):
    wx.EndBusyCursor()


def _CreateWorker(args):
    N, taudiff, linetime, dtype, path = args

    # deltat is linetime
    noisearray = GenerateExpNoise(N, taud=taudiff, deltat=linetime)
    noisearray -= np.min(noisearray)
    noisearray *= 30. / np.max(noisearray)
    #noisearray += 5
    noisearray = np.uint32(noisearray)

    # Create 32bit and 16bit binary .dat files
    # translate linetime in bins of taud
    ltbin = linetime / 1000
    MakeDat(ltbin, noisearray, dtype, path)
