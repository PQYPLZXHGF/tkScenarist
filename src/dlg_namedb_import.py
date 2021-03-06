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
import csv
import os.path as OP
import tkinter.constants as TK
import tkinter.messagebox as MB
import tkinter.filedialog as FD
import tkRAD.core.async as ASYNC
import tkRAD.core.path as P
from tkRAD.core import tools
import tkRAD.widgets.rad_dialog as DLG


class NameDBImportDialog (DLG.RADButtonsDialog):
    """
        Name database CSV file importation dialog;
    """

    # class constant defs
    BUTTONS = ("OK", )

    DEFAULT_DIR = "^/data/csv"

    FIELD_NAMES = ("name", "gender", "origin", "description")

    FILE_TYPES = (
        (_("CSV files"), "*.csv"),
        (_("Text files"), "*.txt"),
        (_("All files"), "*.*"),
    )


    def _do_import_file (self, fpath, findices):
        """
            effective procedure for importing CSV file into name DB;
        """
        # lock task
        self._slot_pending_task_on()
        # switch import button
        self.BTN_IMPORT.configure(
            text=_("Stop"), command=self.slot_stop_import
        )
        # inits
        self.stop_import = False
        # notify user
        self.show_status(_("importing CSV file, please wait..."))
        # reset progressbar
        self.reset_progressbar()
        # open CSV file
        _csvfile = open(fpath, "r", encoding=ENCODING, newline='')
        # get CSV reader
        _csvreader = csv.reader(_csvfile)
        # first row is header - trap it
        next(_csvreader, None)
        # switch off auto_commit mode
        self.database.auto_commit = False
        # enter the loop
        self.async.run_after_idle(
            self._import_loop,
            _csvfile, _csvreader, findices, OP.getsize(fpath), 0
        )
    # end def


    def _do_open_file (self, fpath):
        """
            effective procedure for opening file to import;
        """
        # is a genuine CSV file?
        if self.is_csv(fpath):
            # update options dir
            self.options["dirs"]["namedb_import_dir"] = OP.dirname(fpath)
            # update current path
            self.current_path = fpath
            # update file infos
            self.container.get_stringvar("lbl_file_path")\
                .set(P.shorten_path(fpath, limit=50))
            # show contents preview
            self._fill_preview(fpath)
            # update field assignment order
            self._fill_fields(fpath)
            # prepare to import
            self.BTN_IMPORT.configure(
                text=_("Import"), command=self.slot_file_import
            )
            self.stop_import = False
        # not a CSV file
        else:
            # notify user
            MB.showwarning(
                title=_("Attention"),
                message=_("Invalid CSV file format. Not supported."),
                parent=self,
            )
        # end if
    # end def


    def _fill_combos (self, choices=None, matches=None):
        """
            fills all combobox widgets with same @choices;
        """
        # inits
        _choices = [_("--- not found ---")]
        _choices.extend(choices or [])
        matches = matches or (0,) * len(self.FIELD_NAMES)
        # fill widgets
        for _index, _fname in enumerate(self.FIELD_NAMES):
            _combo = self.get_combobox(_fname)
            _combo.configure(values=_choices)
            _combo.state(["readonly"])
            _combo.current(matches[_index])
        # end for
    # end def


    def _fill_fields (self, fpath):
        """
            fills column assignment order along with CSV file contents;
        """
        # try to get nbr of columns
        with open(fpath, "r", encoding=ENCODING, newline='') as csvfile:
            # get first row
            _row = next(csv.reader(csvfile), [])
            # get nb of fields
            _nbf = len(_row)
            # fill choice list
            _choices = [
                _("Column#{}").format(i + 1) for i in range(_nbf)
            ]
            # set to lower case
            _row = tuple(map(lambda s: str(s).lower(), _row))
            # inits
            _matches = []
            # search matchups
            for _field in self.FIELD_NAMES:
                try:
                    _index = _row.index(_field.lower()) + 1
                except:
                    _index = 0
                # end try
                _matches.append(_index)
            # end for
        # end with
        # fill widgets
        self._fill_combos(_choices, _matches)
    # end def


    def _fill_preview (self, fpath):
        """
            fills preview Text widget with CSV file contents;
        """
        # inits
        _line = 1
        # enable preview
        self.enable_widget(self.PREVIEW, True)
        self.PREVIEW.delete("1.0", TK.END)
        # fill with some rows
        with open(fpath, "r", encoding=ENCODING) as txtfile:
            for _row in txtfile:
                self.PREVIEW.insert(TK.END, _row)
                _line += 1
                if _line > 10: break
            # end for
        # end with
        # and so on
        self.PREVIEW.insert(TK.END, "...")
        # disable preview
        self.enable_widget(self.PREVIEW, False)
    # end def


    def _import_loop (self, csvfile, csvreader, findices, fsize, consumed):
        """
            tkinter-threaded importation loop;
        """
        # consume one row of data
        _row = next(csvreader, None)
        # got data to import?
        if _row and not self.stop_import:
            # update data consumption info
            consumed += len("".join(_row))
            self.set_progressbar(100 * consumed / fsize)
            # inits
            _fields = dict()
            # browse redirection indices
            for _fname, _index in findices.items():
                # redirect field / data
                _fields[_fname] = _row[_index]
            # end for
            # notify user
            self.show_status(
                _("importing name '{name}'").format(**_fields)
            )
            # try out
            try:
                # import data into database
                self.database.import_character_name(**_fields)
            # caught exception
            except:
                print("[WARNING]\tFailed to import row:", _fields)
            # end try
            # commit data each kilobyte
            if int(consumed) % 1024 == 0:
                # commit
                self.database.commit()
            # end if
            # loop once again
            self.async.run_after_idle(
                self._import_loop,
                csvfile, csvreader, findices, fsize, consumed
            )
        # time to close
        else:
            # commit last transaction
            self.database.commit()
            # switch on auto_commit mode
            self.database.auto_commit = True
            # close CSV file
            csvfile.close()
            # stopped by user?
            if self.stop_import:
                # notify user
                self.show_status(_("importation stopped by user."))
            else:
                # notify user
                self.show_status(_("importation succeeded. OK."))
                # set progressbar to max value
                self.set_progressbar(100)
            # end if
            # release task
            self._slot_pending_task_off()
        # end if
    # end def


    def bind_events (self, **kw):
        """
            event bindings;
        """
        # app-wide event bindings
        self.events.connect_dict(
            {
                "Dialog:Import:File:Browse": self.slot_file_browse,
                "Dialog:Import:File:Import": self.slot_file_import,
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
        # stop all pending threads
        self.stop_threads()
        # succeeded
        return True
    # end def


    def get_combobox (self, field_name):
        """
            returns combobox widget based on @field_name;
        """
        return getattr(self.container, "column_{}".format(field_name))
    # end def


    def get_field_indices (self):
        """
            gathers all user input field names for importation process;
        """
        # inits
        _indices = dict()
        # browse user inputs
        for _fname in self.FIELD_NAMES:
            # get widget
            _combo = self.get_combobox(_fname)
            # get index
            _index = _combo.current()
            # got field redirection?
            if _index:
                # add to field indices
                _indices[_fname] = _index - 1
            # end if
        # end for
        # return results
        return _indices
    # end def


    def init_widget (self, **kw):
        r"""
            widget main inits;
        """
        # super class inits
        super().init_widget(
            # looks for ^/xml/widget/dlg_namedb_import.xml
            xml="dlg_namedb_import",
        )
        # member inits
        self.async = ASYNC.get_async_manager()
        self.current_path = ""
        self.database = self.tk_owner.database
        self.stop_import = False
        self.DEFAULT_DIR = P.normalize(self.DEFAULT_DIR)
        # dialog widgets
        self.BTN_IMPORT = self.container.btn_import
        self.PREVIEW = self.container.text_fc_preview
        self.PROGRESSBAR = self.container.pgbar_import
        self.PBAR_VALUE = self.container.get_stringvar("pgbar_value")
        self.STATUS = self.container.get_stringvar("lbl_status")
        # reset combos
        self._fill_combos()
        # event bindings
        self.bind_events(**kw)
    # end def


    def show_status (self, message):
        """
            shows status message in importing zone;
        """
        # show status message
        self.STATUS.set(str(message))
    # end def


    def is_csv (self, fpath):
        """
            returns True if @fpath is evaluated to be a CSV file
            format, False otherwise;
        """
        # try to sniff dialect in file
        with open(fpath, "r", encoding=ENCODING, newline='') as csvfile:
            try:
                csv.Sniffer().sniff(csvfile.read(1024))
                return True
            except:
                return False
            # end try
        # end with
    # end def


    def reset_progressbar (self, *args, **kw):
        """
            event handler: resets progressbar to indeterminate mode;
        """
        # inits
        self.set_progressbar(0)
        # set indeterminate mode
        self.PROGRESSBAR.configure(mode="indeterminate")
        # start animation
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


    def slot_file_browse (self, *args, **kw):
        """
            event handler: shows a file dialog for importing file
            selection;
        """
        # init
        _path = FD.askopenfilename(
            title=_("Please, select a file to import"),
            initialdir=self.options.get(
                "dirs", "namedb_import_dir", fallback=self.DEFAULT_DIR
            ),
            filetypes=self.FILE_TYPES,
            multiple=False,
            parent=self,
        )
        # user selected a path?
        if _path:
            # do open file for importation
            self._do_open_file(_path)
        # end if
    # end def


    def slot_file_import (self, *args, **kw):
        """
            event handler: launches importation procedure;
        """
        # nothing selected?
        if not self.current_path:
            # notify user
            MB.showwarning(
                title=_("Attention"),
                message=_(
                    "Please, select a comma-separated "
                    "values (CSV) file to import."
                ),
                parent=self,
            )
        # got file path
        else:
            # get field redirections from user input
            _indices = self.get_field_indices()
            # nothing at all?
            if not _indices:
                # notify user
                MB.showwarning(
                    title=_("Attention"),
                    message=_("Nothing to import."),
                    parent=self,
                )
            # must have a 'name' field to import
            elif "name" not in _indices:
                # notify user
                MB.showwarning(
                    title=_("Attention"),
                    message=_(
                        "Cannot import names without "
                        "a valid 'name' field."
                    ),
                    parent=self,
                )
            # all is okay
            else:
                # do import
                self._do_import_file(self.current_path, _indices)
            # end if
        # end if
    # end def


    def slot_stop_import (self, *args, **kw):
        """
            event handler: asks for stopping threaded importation loop;
        """
        # inits
        self.stop_import = True
    # end def


    def stop_threads (self, *args, **kw):
        """
            event handler: stops and locks all pending threads;
        """
        self.async.lock(self._import_loop)
    # end def


    def validate_dialog (self, tk_event=None, *args, **kw):
        r"""
            user dialog validation method;
            this is a hook called by '_slot_button_ok()';
            this *MUST* be overridden in subclass;
            returns True on success, False otherwise;
        """
        # pending task control
        if not self.verify_pending_task():
            # stop all pending threads
            self.stop_threads()
            # all is good
            return True
        # end if
        # do not quit
        return False
    # end def

# end class NameDBImportDialog
