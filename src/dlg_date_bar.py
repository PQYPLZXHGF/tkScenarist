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
from datetime import date
from calendar import month_name
import tkRAD.widgets.rad_dialog as DLG


class DateBarDialog (DLG.RADButtonsDialog):
    """
        Resources Planning Date Bar edition dialog;
    """

    # class constant defs
    BUTTONS = ("OK", "Cancel")
    DATE_ERROR = _("invalid date")


    def bind_events (self, **kw):
        """
            event bindings;
        """
        # tkinter widget event bindings
        self.bind("<Escape>", self._slot_button_cancel)
    # end def


    def date_error (self, cvar):
        """
            shows error message at erroneous date input field;
        """
        cvar.set(self.DATE_ERROR)
        self.after(2000, cvar.set, "")
        return False
    # end def


    def get_date (self, group):
        """
            retrieves a datetime.date object from date data stored in
            @group;
        """
        # inits
        _day, _month, _year = group
        # retrieve date
        return date(
            int(_year.get()), _month.current() + 1, int(_day.get())
        )
    # end def


    def init_combos (self, *groups):
        """
            sets default values for date combos groups;
            group is combo tuple(day, month, year);
        """
        # inits
        _DAYS = ["{:02d}".format(i) for i in range(1, 32)]
        _MONTHS = list(month_name)[1:]
        _YEAR = date.today().year
        _YEARS = list(range(_YEAR - 1, _YEAR + 2))
        # browse groups
        for _group in groups:
            # inits
            _day, _month, _year = _group
            # day values
            _day.configure(values=_DAYS, state="readonly")
            _day.current(0)
            # month values
            _month.configure(values=_MONTHS, state="readonly")
            _month.current(0)
            # year values
            _year.configure(values=_YEARS, state="readonly")
            _year.current(0)
        # end for
    # end def


    def init_widget (self, **kw):
        """
            widget main inits;
        """
        # super class inits
        super().init_widget(
            # looks for ^/xml/widget/dlg_date_bar.xml
            xml="dlg_date_bar",
        )
        # member inits
        self.datebar_tag = kw.get("datebar_tag")
        _w = self.container
        self.LBL_NAME = _w.get_stringvar("item_name")
        self.LBL_NAME.set(kw.get("item_name") or "sample demo")
        self.OPT_STATUS = _w.get_stringvar("opt_status")
        self.OPT_STATUS.set(
            kw.get("status") == "N/A" and "N/A" or "OK"
        )
        self.CBO_BEGIN = (
            _w.combo_begin_day,
            _w.combo_begin_month,
            _w.combo_begin_year,
        )
        self.LBL_ERR_BEGIN = _w.get_stringvar("lbl_begin_error")
        self.CBO_END = (
            _w.combo_end_day,
            _w.combo_end_month,
            _w.combo_end_year,
        )
        self.LBL_ERR_END = _w.get_stringvar("lbl_end_error")
        self.init_combos(self.CBO_BEGIN, self.CBO_END)
        self.reset_combos(**kw)
        # event bindings
        self.bind_events(**kw)
    # end def


    def reset_combos (self, **kw):
        """
            resets date combos to fit real date values;
        """
        # inits
        _today = date.today()
        _begin = kw.get("date_begin") or _today
        _end = kw.get("date_end") or _today
        # reset dates
        self.reset_date(_begin, self.CBO_BEGIN)
        self.reset_date(_end, self.CBO_END)
    # end def


    def reset_date (self, cdate, group):
        """
            resets @cdate datetime.date object into combo @group;
        """
        # date inits
        _cday = cdate.day
        _cmonth = cdate.month
        _cyear = cdate.year
        _YEAR = date.today().year
        _ymin = min(_YEAR - 1, _cyear)
        _ymax = max(_YEAR + 5, _cyear)
        # combo inits
        _day, _month, _year = group
        # reset date
        _day.current(_cday - 1)
        _month.current(_cmonth - 1)
        _year.configure(values=list(range(_ymin, _ymax + 1)))
        _year.set(_cyear)
    # end def


    def validate_dialog (self, tk_event=None, *args, **kw):
        """
            user dialog validation method;
            this is a hook called by '_slot_button_ok()';
            this *MUST* be overridden in subclass;
            returns True on success, False otherwise;
        """
        # inits
        try:
            _begin = self.get_date(self.CBO_BEGIN)
        except:
            return self.date_error(self.LBL_ERR_BEGIN)
        # end try
        try:
            _end = self.get_date(self.CBO_END)
        except:
            return self.date_error(self.LBL_ERR_END)
        # end try
        # incorrect interval?
        if _begin > _end:
            # swap dates
            _begin, _end = _end, _begin
        # end if
        # notify app
        self.events.raise_event(
            "Dialog:DateBar:Validate",
            datebar_tag=self.datebar_tag,
            item_name=self.LBL_NAME.get(),
            status=self.OPT_STATUS.get(),
            date_begin=_begin,
            date_end=_end,
        )
        # all is good
        return True
    # end def

# end class DateBarDialog
