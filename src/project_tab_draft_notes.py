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
import json
import tkRAD


class ProjectTabDraftNotes (tkRAD.RADXMLFrame):
    """
        application's project tab class;
    """

    def bind_events (self, **kw):
        """
            app-wide event bindings;
        """
        self.events.connect_dict(
            {
                "Pitch:Template:Insert": self.slot_template_insert,

                "Project:Modified": self.slot_project_modified,

                "Tab:Reset": self.slot_tab_reset,
            }
        )
    # end def


    def get_file_contents (self, fname):
        """
            returns file contents;
        """
        # inits
        _dict = {
            fname["text"]: self.text_get_contents(
                self.text_draft_notes
            ),
            # for future implementations
            fname["data"]: json.dumps(
                {}
            ),
        }
        # always return a dict
        return _dict
    # end def


    def init_widget (self, **kw):
        """
            hook method to be reimplemented by subclass;
        """
        # member inits
        self.mainwindow = self.services.get_service("mainwindow")
        self.mainframe = self.mainwindow.mainframe
        self.text_clear_contents = self.mainwindow.text_clear_contents
        self.text_get_contents = self.mainwindow.text_get_contents
        self.text_set_contents = self.mainwindow.text_set_contents
        # looks for ^/xml/widget/tab_draft_notes.xml
        self.xml_build("tab_draft_notes")
        # event bindings
        self.bind_events(**kw)
    # end def


    def setup_tab (self, fname, archive):
        """
            tab setup along @fname and @archive contents;
        """
        # inits
        _get_fc = lambda f: archive.read(f).decode(ENCODING)
        # get text contents
        _text = _get_fc(fname["text"])
        # get data (future implementations)
        _data = json.loads(_get_fc(fname["data"]))
        # set text widget contents
        self.text_set_contents(self.text_draft_notes, _text)
    # end def


    def slot_project_modified (self, *args, flag=True, **kw):
        """
            event handler for project's modification flag;
        """
        # reset status
        self.text_draft_notes.edit_modified(flag)
    # end def


    def slot_tab_reset (self, *args, **kw):
        """
            event handler: reset tab to new;
        """
        # reset Text widget
        self.text_clear_contents(self.text_draft_notes)
    # end def


    def slot_template_insert (self, *args, notes=None, **kw):
        """
            event handler for pitch template dialog text insertion;
        """
        # param controls
        if notes:
            # insert text
            self.text_set_contents(self.text_draft_notes, notes)
            # notify application
            self.events.raise_event("Project:Modified")
        # end if
    # end def

# end class ProjectTabDraftNotes
