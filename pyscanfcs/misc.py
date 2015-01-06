# -*- coding: utf-8 -*-
"""
    PyScanFCS

    Module misc

    (C) 2012 Paul Müller

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License 
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function, division

import codecs
from distutils.version import LooseVersion # For version checking
import numpy as np
import os
import platform
import sys
import tempfile
import urllib2
import webbrowser
import wx                               # GUI interface wxPython
import wx.html
import wx.lib.delayedresult as delayedresult


from . import doc                          # Documentation/some texts
# The icon file was created with
# img2py -i -n Main PyScanFCS_icon.png icon.py
from . import icon                         # Contains the program icon
from . import edclasses


class UpdateDlg(wx.Frame):
    def __init__(self, parent, valuedict):
        
        description = valuedict["Description"]
        homepage = valuedict["Homepage"]
        githome = valuedict["Homepage_GIT"]
        changelog = valuedict["Changelog"]
        pos = parent.GetPosition()
        pos = (pos[0]+100, pos[1]+100)
        wx.Frame.__init__(self, parent, wx.ID_ANY, title="Update", 
                          size=(250,180), pos=pos)
        self.changelog = changelog
        # Fill html content
        html = wxHTML(self)
        string =             '' +\
            "<b> PyScanFCS <br></b>" +\
            "Your version: " + description[0]+"<br>" +\
            "Latest version: " + description[1]+"<br>" +\
            "(" + description[2]+")<br><p><b>"
        if len(homepage) != 0:
            string = string + '<a href="'+homepage+'">Homepage</a><br>'
        if len(githome) != 0:
            string = string + '<a href="'+githome+'">Repository</a><br>'

        if len(changelog) != 0:
            string = string + \
                     '<a href="'+changelog+'">Change Log</a>'
        string = string+'</b></p>'
        html.SetPage(string)
        self.Bind(wx.EVT_CLOSE, self.Close)
        # Set window icon
        ico = getMainIcon()
        wx.Frame.SetIcon(self, ico)


    def Close(self, event):
        if len(self.changelog) != 0:
            # Cleanup downloaded file, if it was downloaded
            if self.changelog != doc.StaticChangeLog:
                os.remove(self.changelog)
        self.Destroy()


class wxHTML(wx.html.HtmlWindow):
    def OnLinkClicked(parent, link):
         webbrowser.open(link.GetHref())


class ArtificialDataDlg(wx.Frame):
    # This tool is derived from a wx.frame.
    def __init__(self, parent):
        self.parent = parent
        # Get the window positioning correctly
        pos = self.parent.GetPosition()
        pos = (pos[0]+100, pos[1]+100)
        wx.Frame.__init__(self, parent=self.parent,
                          title="Create artificial test data", pos=pos, 
                  style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
        
        ## Content
        self.panel = wx.Panel(self)
        
        topSizer = wx.BoxSizer(wx.VERTICAL)
        

        topSizer.Add(wx.StaticText(self.panel,
                          label="Create artificial test data\n"+
                          "with exponentially correlated noise.\n"))
        
        colsizer = wx.FlexGridSizer(4, 2)
        
        # decay time
        colsizer.Add( wx.StaticText(self.panel,
                                    label=u"Correlation time [ms]: "))
        self.WXDecay = edclasses.FloatSpin(self.panel,
                                          value="100")
        colsizer.Add(self.WXDecay)

        # line scanning time
        colsizer.Add( wx.StaticText(self.panel,
                                    label=u"Scan cycle time [ms]: "))
        self.WXLine = edclasses.FloatSpin(self.panel,
                                          value="0.714")
        colsizer.Add(self.WXLine)

        # number of samples
        colsizer.Add( wx.StaticText(self.panel,
                                    label=u"Number of samples: "))
        self.WXNumber = wx.SpinCtrl(self.panel, -1, min=10000,
                                    max=500000000, value="500000")
        colsizer.Add(self.WXNumber)

        # data format
        colsizer.Add(wx.StaticText(self.panel, label="Data format: "))
        self.WXDropInt = wx.ComboBox(self.panel, -1, "uint16", (15,30),
                                   wx.DefaultSize, ["uint16", "uint32"],
                                   wx.CB_DROPDOWN|wx.CB_READONLY)
        colsizer.Add(self.WXDropInt)

        topSizer.Add(colsizer)

        btndo = wx.Button(self.panel, wx.ID_CLOSE, 'Create .dat file')
        # Binds the button to the function - close the tool
        
        self.Bind(wx.EVT_BUTTON, self.OnCreateFile, btndo)
        
        topSizer.Add(btndo)
        self.panel.SetSizer(topSizer)
        topSizer.Layout()
        topSizer.Fit(self)
        #self.SetMinSize(colsizer.GetMinSizeTuple())
        #Icon
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
           wx.SAVE|wx.FD_OVERWRITE_PROMPT)
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
    # time trace
    t = np.arange(N_steps)
    # AR-1 processes - what does that mean?
    # time constant (inverse of correlationtime taud)
    g = 1./taud
    # variance
    s0 = variance
    
    # normalization factor (memory of the trace)
    exp_g = np.exp(-g*dt)
    one_exp_g = 1-exp_g
    z_norm_factor = np.sqrt(1-np.exp(-2*g*dt))/one_exp_g
    
    # create random number array
    # generates random numbers in interval [0,1)
    randarray = np.random.random(N_steps)
    # make numbers random in interval [-1,1)
    randarray = 2*(randarray-0.5)
    
    # simulate exponential random behavior
    z = np.zeros(N_steps)
    z[0] = one_exp_g*randarray[0]
    for i in np.arange(N_steps-1)+1:
        z[i] = exp_g*z[i-1] + one_exp_g*randarray[i]
        
    z = z * z_norm_factor*s0
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
    data = list()
    timeticks = linetime*newclock*1e6 # 60MHz
    half1 = np.ceil(timeticks/2)
    half2 = np.floor(timeticks/2)
    for i in np.arange(len(noisearray)):
        # Create a line
        N = noisearray[i]
        if N == 0:
            line=np.zeros(1, dtype=dtype)
            # Only one event at the far corner
            line[0] = timeticks
            line.tofile(NewFile)
        else:
            line = np.ones(N+1, dtype=dtype)
            # events are included between two far events
            line[0] = half1-len(line)
            line[-1] = half2
            line.tofile(NewFile)
    NewFile.close()


def removewrongUTF8(name):
    newname = u""
    for char in name:
       try:
           uchar = codecs.decode(char, "UTF-8")
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
    image = wx.ImageFromBitmap(iconBMP)
    image = image.Scale(pxlength, pxlength, wx.IMAGE_QUALITY_HIGH)
    iconBMP = wx.BitmapFromImage(image)
    iconICO = wx.IconFromBitmap(iconBMP)
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
    noisearray *= 30./np.max(noisearray)
    #noisearray += 5
    noisearray = np.uint32(noisearray)

    # Create 32bit and 16bit binary .dat files
    # translate linetime in bins of taud
    ltbin = linetime / 1000
    data = MakeDat(ltbin, noisearray, dtype, path)




def Update(parent):
    """ This is a thread for _Update """
    parent.StatusBar.SetStatusText("Connecting to server...")
    delayedresult.startWorker(_UpdateConsumer, _UpdateWorker,
                              wargs=(parent,), cargs=(parent,))


def _UpdateConsumer(delayedresult, parent):
    results = delayedresult.get()
    dlg = UpdateDlg(parent, results)
    dlg.Show()
    parent.StatusBar.SetStatusText("...update status: "+results["Description"][2])


def _UpdateWorker(parent):
        changelog = ""
        hpversion = None
        # I created this TXT record to keep track of the current web presence.
        try:
            urlopener = urllib2.urlopen(doc.HomePage, timeout=2)
            homepage = urlopener.geturl()
        except:
            homepage = doc.HomePage
        try:
            urlopener2 = urllib2.urlopen(doc.GitHome, timeout=2)
            githome = urlopener2.geturl()
        except:
            githome = ""
        # Find the changelog file
        try:
            responseCL = urllib2.urlopen(homepage+doc.ChangeLog, timeout=2)
        except:
            CLfile = doc.GitChLog
        else:
            fileresponse = responseCL.read()
            CLlines = fileresponse.splitlines()
            # We have a transition between ChangeLog.txt on the homepage
            # containing the actual changelog or containing a link to
            # the ChangeLog file.
            if len(CLlines) == 1:
                CLfile = CLlines[0]
            else:
                hpversion = CLlines[0]
                CLfile = doc.GitChLog
        # Continue version comparison if True
        continuecomp = False
        try:
            responseVer = urllib2.urlopen(CLfile, timeout=2)
        except:
            if hpversion == None:
                newversion = "unknown"
                action = "cannot connect to server"
            else:
                newversion = hpversion
                continuecomp = True
        else:
            continuecomp = True
            changelog = responseVer.read()
            newversion = changelog.splitlines()[0]
        if continuecomp:
            new = LooseVersion(newversion)
            old = LooseVersion(parent.version)
            if new > old:
                action = "update available"
            elif new < old:
                action = "whoop you rock!"
            else:
                action = "state of the art"
        description = [parent.version, newversion, action]
        if len(changelog) != 0:
            changelogfile = tempfile.mktemp()+"_PyScanFCS_ChangeLog"+".txt"
            clfile = open(changelogfile, 'wb')
            clfile.write(changelog)
            clfile.close()            
        else:
            changelogfile=doc.StaticChangeLog
        results = dict()
        results["Description"] = description
        results["Homepage"] = homepage
        results["Homepage_GIT"] = githome
        results["Changelog"] = changelogfile
        return results
