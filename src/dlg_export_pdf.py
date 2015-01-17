#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    tkScenarist - screen writing made simpler

    Copyright (c) 2014+ Raphaël Seban <motus@laposte.net>

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of
    the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.

    If not, see http://www.gnu.org/licenses/
"""

# lib imports
import tkinter.constants as TK
import tkRAD.widgets.rad_dialog as DLG
import tkRAD.core.async as ASYNC
from tkRAD.core import tools
from . import pdf_export as PDF


class ExportPDFDialog (DLG.RADButtonsDialog):
    """
        Resources Planning Date Bar edition dialog;
    """

    # class constant defs
    BUTTONS = ("OK", )

    DOC_NAMES = (
        "characters", "draft_notes", "pitch_concept", "resources",
        "scenario", "storyboard",
    )


    def _export_loop (self, kw):
        """
            tk exportation loop;
            internal use;
        """
        print("_export_loop")
        # loop controls
        if self.__keep_looping:
            # inits
            _export_list = kw.get("export_list")
            _step = tools.ensure_int(kw.get("step"))
            print("export list:", _export_list)
            # loop again
            self.async.run_after(100, self._export_loop, kw)
        # end of exportation process
        else:
            # release important task
            self.events.raise_event("DialogPendingTaskOff")
            # reset button
            self.enable_button("OK")
            # reset export button
            self.BTN_EXPORT.configure(
                text=_("Export"), command=self.slot_export_pdf
            )
        # end if
    # end def


    def bind_events (self, **kw):
        """
            event bindings;
        """
        # app-wide events
        self.events.connect_dict(
            {
                "Dialog:ExportPDF:Export": self.slot_export_pdf,
            }
        )
        # tkinter widget event bindings
        self.bind("<Escape>", self._slot_button_ok)
    # end def


    def cancel_dialog (self, tk_event=None, *args, **kw):
        r"""
            user dialog cancellation method;
            this is a hook called by '_slot_button_cancel()';
            this *MUST* be overridden in subclass;
            returns True on success, False otherwise;
        """
        # put here your own code in subclass
        self.slot_stop_export()
        self.async.stop(self._export_loop)
        # succeeded
        return True
    # end def


    def get_export_list (self):
        """
            retrieves user's exportation list and returns a list of doc
            names to export;
        """
        # inits
        _list = []
        _sel = lambda n: self.container.get_stringvar("chk_" + n).get()
        # browse doc names
        for _name in self.DOC_NAMES:
            # user selected?
            if _sel(_name):
                # append to list
                _list.append(_name)
            # end if
        # end for
        # get list
        return _list
    # end def


    def init_widget (self, **kw):
        """
            widget main inits;
        """
        # super class inits
        super().init_widget(
            # looks for ^/xml/widget/dlg_export_pdf.xml
            xml="dlg_export_pdf",
        )
        # member inits
        self.mainframe = self.tk_owner.mainframe
        self.async = ASYNC.get_async_manager()
        self.__keep_looping = False
        # widget inits
        _w = self.container
        self.LBL_STATUS = _w.get_stringvar("lbl_export_status")
        self.PROGRESSBAR = _w.progressbar_export
        self.PBAR_VALUE = _w.get_stringvar("pbar_value")
        self.BTN_EXPORT = _w.btn_export
        # event bindings
        self.bind_events(**kw)
    # end def


    def progressbar_wait (self):
        """
            simulates progressbar waiting for ops;
        """
        # stop animation
        self.PROGRESSBAR.stop()
        # set indeterminate mode
        self.PROGRESSBAR.configure(mode="indeterminate")
        # restart animation
        self.PROGRESSBAR.start()
    # end def


    def set_progressbar (self, value):
        """
            sets progressbar to @value (between 0 and 100);
        """
        # set determinate mode
        self.PROGRESSBAR.configure(mode="determinate")
        # stop animation
        self.PROGRESSBAR.stop()
        # set value
        self.PBAR_VALUE.set(str(tools.ensure_int(value)))
    # end def


    def show_status (self, message):
        """
            shows message in exportation status;
        """
        self.LBL_STATUS.set(str(message))
    # end def


    def slot_export_pdf (self, *args, **kw):
        """
            event handler: button clicked;
        """
        print("slot_export_pdf")
        # switch on important task
        self.events.raise_event("DialogPendingTaskOn")
        # disable button
        self.disable_button("OK")
        # change export button
        self.BTN_EXPORT.configure(
            text=_("Stop"), command=self.slot_stop_export,
        )
        # notify
        self.show_status(
            _("Trying to export selected items, please wait.")
        )
        # waiting for ops
        self.progressbar_wait()
        # inits
        self.__keep_looping = True
        # launch exportation loop
        self.async.run_after_idle(
            self._export_loop,
            dict(export_list=self.get_export_list())
        )
    # end def

    def slot_stop_export (self, *args, **kw):
        """
            event handler: breaking exportation loop;
        """
        print("slot_stop_export")
        self.__keep_looping = False
    # end def

# end class ExportPDFDialog
