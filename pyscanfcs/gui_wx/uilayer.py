"""uilayer

python user interface layer to monitor progress of long-running
algorithms
"""
import os
import sys
import warnings

__all__ = ["dummy", "ui", "stdout"]

try:
    import wx
except:
    pass
else:
    __all__ += ["wxdlg"]


class base_ui():
    """
        This is the main class from which all interfaces are derived.
        It is quiet, meaning it does not output any progress data, but
        it will display warings and errors in the console.
    """

    def __init__(self, steps=None, pids=None, progress=None,
                 subpids=None, show_warnings=True, totalsteps=None,
                 dirname=None, **kwargs):
        """
            Creates an instance and sets initial parameters for progress
            dialogs (optional).


            Parameters:
            -----------
            pids, steps, progress, subpids : optional
                See documentation of self.SetProgress
            show_warnings : bool
                Display warnings of/in the interface.
            totalsteps : int or None
                Known number of total steps of all progresses. This
                number can be larger than the sum of all steps,
                inferring knowledge on the progresses to come.


            See Also
            --------
            SetProgress : Sets initial parameters manually
        """
        if dirname is None:
            self._dirname = os.path.expanduser("~")
        self._abortlist = list()
        self._totalsteps = totalsteps
        self._currentstep = 0
        self._single_progress = False
        self.ShowWarnings(show_warnings)
        self.SetProgress(steps=steps,
                         pids=pids,
                         progress=progress,
                         subpids=subpids)

    def GetDir(self):
        """ Returns the current working directory.
        """
        return self._dirname

    def Iterate(self, pid=None, subpid=0, **kwargs):
        """ Iterate progress.

        Increments the "current step" of a progress by one.
        Warns the user if the step is above "total steps".

        Also looks for the pid in self._abortlist and returns it to
        the process to stop it.
        """
        if self._totalsteps is not None:
            self._currentstep += 1

        if pid is None:
            if self._single_progress == False:
                self.warn("I do not know which progress to iterate." +
                          " Please specify the kwarg pid.")
            pid = 0

        pid = int(pid)
        subpid = int(subpid)

        for i in range(len(self._pids)):
            if self._pids[i] == pid and self._subpids[i] == subpid:
                self._progress[i] += 1

        self.Update()

        if pid in self._abortlist:
            # Try to stop the process if it supports that.
            # Returning anything else but None will stop the process.
            return pid

    def Finalize(self, pid=None, subpid=0, **kwargs):
        """ Triggers output that a process is finished
        """
        pass

    def SelectPath(self, **kwargs):
        """ Select a file or folder from the file system.

        This does not do anything here.
        """
        pass

    def SetDir(self, dirname):
        """ Sets the current working directory.
        """
        self._dirname = dirname

    def SetProgress(self, steps=None, pids=None, progress=None,
                    subpids=None, **kwargs):
        """
            Set the initial parameters of the processes that are to be
            monitored by this class.


            Parameters
            ----------
            pids : Array-like dtype(int) or int, length N
                Process identifiers
            steps : Array-like dtype(int) or int, length N
                Maximum number of steps for each process
            progress : Array-like dtype(int) or int, length N
                Current step in the progress counting up until `steps`
            subpids : Array-like dtype(int) or int, length N
                Sub-process identifiers - useful for multithreading

            The following kwargs combinations are possible:
                1. pids, steps, progress, subpids all `None`
                    Nothing will happen
                2. pids, steps, progress, subpids all some int
                    Only one process of unknown length
                3. pids, steps, progress, subpids all integer `list`s
                    Multiple processes are assumed
                4. pids, progress, subpids all `None` and steps int
                    Only one process of known length
                5. pids, progress, subpids all `None` and steps `list`
                    Multiple processes of known length - internally
                    the processes get `pids` that are enumerated from
                    zero onwards and `progress` is set no zeros.

            Returns
            -------
            success : bool
                True if data was set and False if nothing was set.
        """
        self._single_progress = False
        self._no_data = False
        self._known_length = False
        if (pids is None and steps is None and progress is None):
            # 1. Nothing will happen
            self._no_data = True
            return False
        elif (pids is not None and steps is not None and
              progress is not None):
            # 2. Only one process
            # or
            # 3. Multiple processes are assumed
            self._known_length = False
        elif (pids is None and steps is not None and progress is None):
            self._known_length = True
            if isinstance(steps, (int, float, complex)):
                # 4. Only one process of known length
                self._single_progress = True
                pids = 0
                progress = 0
            else:
                # 5. Multiple processes of known length - internally
                #    the processes get `pids` that are enumerated from
                #    zero onwards and `progress` is set no zeros.
                pids = range(len(steps))
                progress = [0] * len(steps)
        else:
            raise NameError("Your set of parameters is invalid.")

        # Convert input to list
        if isinstance(pids, (int, float, complex)):
            # Only one progress
            self._single_progress = True
            pids = [pids]
        if isinstance(steps, (int, float, complex)):
            steps = [steps]
        if isinstance(progress, (int, float, complex)):
            progress = [progress]
        if isinstance(subpids, (int, float, complex)):
            subpids = [subpids]

        self._pids = pids
        # Defines how many steps should be used to split the total
        # computation. The function self.progress will be used to
        # follow the steps of the algorithm.
        self._steps = steps
        self._progress = progress

        if subpids is None:
            self._subpids = [0] * len(self._pids)
        else:
            self._subpids = subpids

        return True

    def ShowWarnings(self, show_warnings):
        """
            show_warnings : bool
                enable or disable warning
        """
        self._show_warnings = show_warnings

    def Update(self, **kwargs):
        """  Read and write from and to the user interface

        This does not do anything here.
        """
        pass

    def warn(self, msg):
        """ Warns the user when there is a problem. """
        if self._show_warnings:
            warnings.warn(msg)


class dummy(object):
    """
        This is a dummy class that can be used to improve speed.
        There will be no output.
    """

    def __init__(self, *args, **kwargs):
        pass

    def Finalize(self, *args, **kwargs):
        pass

    def Iterate(self, *args, **kwargs):
        pass

    def SelectPath(self, *args, **kwargs):
        pass

    def SetDir(self, *args, **kwargs):
        pass

    def SetProgress(self, *args, **kwargs):
        pass

    def ShowWarnings(self, *args, **kwargs):
        pass

    def Update(self, *args, **kwargs):
        pass

    def warn(self, *args, **kwargs):
        pass


class stdout(base_ui):
    """ Writes progress into standard output.

    """

    def __init__(self, **kwargs):
        """ Stuff that needs to be done in the beginning.

        """
        base_ui.__init__(self, **kwargs)
        self._maxlength = get_terminal_width()

    def Finalize(self, pid=None, subpid=0, name=None, **kwargs):
        """ Triggers output when a process is finished.

        """
        if pid is None:
            self.warn("I do not know which progress to finalize." +
                      " Please specify the kwarg pid.")

        pid = int(pid)
        subpid = int(subpid)

        msg = "Progress finished: {}-{}".format(pid, subpid)
        if name is not None:
            msg += " ({})".format(name)
        dn = max(self._maxlength - len(msg), 0)

        sys.stdout.write("\r{}{}\n".format(msg, dn * " "))
        sys.stdout.flush()

    def Update(self, **kwargs):
        """ Read and write from and to the user interface.

        The algorithm wants to tell the user something.
        We use the last line of the standard output to write the
        progress of all algorithms.
        """
        startline = u"Progress: "
        msg = startline
        if self._single_progress:
            if self._steps[0] == 0:
                perc = int(self._progress[0])
                msg += u"{}".format(perc)
            else:
                perc = self._progress[0] / self._steps[0] * 100.
                msg += u"{:0.2f}%".format(perc)
        else:
            for i in range(len(self._pids)):
                # compute percentage
                if self._pids[i] != -1:
                    if self._steps[i] == 0:
                        perc = int(self._progress[i])
                        msg += u"{}-{}@{}|".format(
                            self._pids[i], self._subpids[i], perc)
                    else:
                        perc = self._progress[i] / self._steps[i] * 100.
                        msg += u"{}-{}@{:0.2f}%|".format(
                            self._pids[i], self._subpids[i], perc)
        msg = msg.strip(" |")

        dn = max(self._maxlength - len(msg), 0)

        newline = "\r{}{}".format(msg, dn * " ")

        if len(newline) > self._maxlength + 1:
            warnings.warn("Terminal width too small. Output cropped.")
            newline = newline[:self._maxlength - 1]

        if newline.strip() == startline.strip():
            newline = self._maxlength * " " + "\r"

        sys.stdout.write(newline)
        sys.stdout.flush()


class wxdlg(base_ui):
    """ Displays propgress in a wx dialog window.

    Can be used from within a wx.App.
    """

    def __init__(self, parent=None, title="Progress", **kwargs):
        """ Stuff that needs to be done in the beginning.

        """
        self.parent = parent
        self.title = title
        base_ui.__init__(self, **kwargs)

    def Destroy(self):
        """ Destroys the wxdlg class.
        """
        try:
            self.Finalize()
        except:
            pass

    def Finalize(self, pid=None, subpid=0, name=None, **kwargs):
        """ Triggers output when a process is finished.

        """
        if self._single_progress:
            self.dlg.Destroy()
        elif (self._totalsteps is not None and
              self._totalsteps <= self._currentstep):
            self.dlg.Destroy()
        else:
            self.Update()

    def SelectPath(self, dirname=None, title="Open file",
                   wildcards=["*"], fname="All files", mode="r",
                   **kwargs):
        """ Select a file or folder from the file system.

        Opens a wx.FileDialog for selecting files.

        Parameters
        ----------
        mode : str
            File mode operations read "r" or write "w" or
            read multiple files "mr".

        Returns the files in a list.
        """
        if dirname is None:
            dirname = self._dirname
        front = " ("
        rear = ")|"
        for wc in wildcards:
            front += "*.{}, ".format(wc)
            rear += ";*{}".format(wc)
        front.strip(", ")
        wcstring = fname + front + rear

        if mode == "r":
            wxmode = wx.FD_OPEN
        else:
            raise NotImplementedError(
                "Mode '{}' not supported".format(mode))
        dlg = wx.FileDialog(self.parent, title, dirname, "",
                            wcstring, wxmode)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self._dirname = os.path.split(path)[0]
            dlg.Destroy()
            return path
        else:
            return

    def SetProgress(self, **kwargs):
        """ Sets progress data from base_ui and dialog parameters

        """
        if base_ui.SetProgress(self, **kwargs):

            style = wx.PD_SMOOTH | wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT

            if self._known_length:
                style |= wx.PD_REMAINING_TIME

            if self._totalsteps is not None:
                maxsteps = self._totalsteps
            else:
                maxsteps = 0
                for i in self._steps:
                    maxsteps += i

            self._total_counter = 0

            # known length?
            title = self.title
            if not self._single_progress:
                title += " ({} processes)".format(len(self._steps))

            self.dlg = wx.ProgressDialog(
                title=title,
                message="Running : ",
                maximum=maxsteps,
                parent=self.parent,
                style=style)

            self.dlg.SetMinSize((300 + 20 * len(self._steps), 80))

    def Update(self, **kwargs):
        """ Read and write from and to the user interface.

        Checks if the user has pressed 'Cancel' and updates the
        Progress bar.
        """
        self._total_counter += 1

        msg = "Running : "

        if self._single_progress:
            if self._known_length:
                msg += "PID {}-{}".format(self._pids[0],
                                          self._subpids[0])
            else:
                msg += "PID {}-{}@{}".format(self._pids[0],
                                             self._subpids[0],
                                             self._progress[0])
        else:
            for i in range(len(self._pids)):
                if self._pids[i] != -1:
                    if self._known_length:
                        msg += u"PID {}-{}@{}, ".format(
                            self._pids[i], self._subpids[i], self._progress[i])
                    else:
                        msg += u"PID {}-{}, ".format(
                            self._pids[i], self._subpids[i])

        msg = msg.strip(" ,")

        if self._known_length:
            cont = self.dlg.Update(self._total_counter, msg)[0]
        else:
            cont = self.dlg.UpdatePulse(newmsg=msg)[0]

        if cont is False:
            # On next iteration, algorithms can abort if they
            # support it.
            self._abortlist += self._pids


def get_terminal_size(fd=1):
    """
    Returns height and width of current terminal. First tries to get
    size via termios.TIOCGWINSZ, then from environment. Defaults to 25
    lines x 80 columns if both methods fail.

    :param fd: file descriptor (default: 1=stdout)

    Author: cas (http://blog.taz.net.au/author/cas/)
    """
    try:
        import fcntl
        import termios
        import struct
        hw = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
    except:
        try:
            hw = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            hw = (25, 80)

    return hw


def get_terminal_height(fd=1):
    """
    Returns height of terminal if it is a tty, 999 otherwise

    :param fd: file descriptor (default: 1=stdout)
    """
    if os.isatty(fd):
        height = get_terminal_size(fd)[0]
    else:
        height = 999

    return height


def get_terminal_width(fd=1):
    """
    Returns width of terminal if it is a tty, 999 otherwise

    :param fd: file descriptor (default: 1=stdout)
    """
    if os.isatty(fd):
        width = get_terminal_size(fd)[1]
    else:
        width = 999

    return width
