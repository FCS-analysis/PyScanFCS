"""Edited classes"""
import numpy as np
from wx.lib.agw import floatspin
import wx


class FloatSpin(floatspin.FloatSpin):
    def __init__(self, parent, digits=10, increment=.01, value=1.0):
        floatspin.FloatSpin.__init__(self, parent, digits=digits,
                                     increment=increment, value=value)
        self.Bind(wx.EVT_SPINCTRL, self.increment)

    def increment(self, event=None):
        # Find significant digit
        # and use it as the new increment
        x = self.GetValue()
        if x == 0:
            incre = 0.1
        else:
            digit = int(np.ceil(np.log10(abs(x)))) - 2
            incre = 10**digit
        self.SetIncrement(incre)


class ChoicesDialog(wx.Dialog):
    def __init__(self, parent, dropdownlist, title, text):
        # parent is main frame
        self.parent = parent

        super(ChoicesDialog, self).__init__(parent=parent,
                                            title=title)
        # Get the window positioning correctly
        #pos = self.parent.GetPosition()
        #pos = (pos[0]+100, pos[1]+100)
        # wx.Frame.__init__(self, parent=parent, title=title,
        #         pos=pos, style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)

        #self.Filename = None
        # Controls
        panel = wx.Panel(self)

        # text1
        textopen = wx.StaticText(panel, label=text)
        btnok = wx.Button(panel, wx.ID_OK)
        btnabort = wx.Button(panel, wx.ID_CANCEL)

        # Dropdown
        self.dropdown = wx.ComboBox(panel, -1, "", (15, 30),
                                    wx.DefaultSize, dropdownlist, wx.CB_DROPDOWN | wx.CB_READONLY)
        self.dropdown.SetSelection(0)
        # Bindings
        self.Bind(wx.EVT_BUTTON, self.OnOK, btnok)
        self.Bind(wx.EVT_BUTTON, self.OnAbort, btnabort)

        # Sizers
        topSizer = wx.BoxSizer(wx.VERTICAL)

        topSizer.Add(textopen)
        topSizer.Add(self.dropdown)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(btnok)
        btnSizer.Add(btnabort)

        topSizer.Add(btnSizer)

        panel.SetSizer(topSizer)
        topSizer.Fit(self)
        self.Show(True)

    def OnOK(self, event=None):
        self.SelcetedID = self.dropdown.GetSelection()
        self.EndModal(wx.ID_OK)

    def OnAbort(self, event=None):
        self.EndModal(wx.ID_CANCEL)
