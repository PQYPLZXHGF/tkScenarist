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
import tkinter.messagebox as MB
import tkinter.simpledialog as SD
import tkRAD
import tkRAD.core.async as ASYNC


class ProjectTabStoryboard (tkRAD.RADXMLFrame):
    """
        application's project tab class;
    """

    def auto_save (self, *args, **kw):
        """
            event handler;
            automatically saves data, if any;
        """
        # got selected scene and shot?
        if self.current_scene and self.current_shot:
            pass                                                                # FIXME
        # end if
    # end def


    def bind_events (self, **kw):
        """
            app-wide event bindings;
        """
        self.events.connect_dict(
            {
                "Project:Modified": self.slot_project_modified,

                "Storyboard:Shot:Add": self.slot_shot_add,
                "Storyboard:Shot:Delete": self.slot_shot_delete,
                "Storyboard:Shot:Rename": self.slot_shot_rename,

                "Tab:Reset": self.slot_tab_reset,
            }
        )
        # tkinter event bindings
        self.LBOX_SCENE.bind(
            "<<ListboxSelect>>", self.slot_scene_item_selected
        )
        self.LBOX_SHOT.bind(
            "<<ListboxSelect>>", self.slot_shot_item_selected
        )
        self.TEXT_SHOT.bind("<KeyRelease>", self.slot_on_text_keypress)
    # end def


    def clear_entry (self, *widgets):
        """
            clears contents for entry widget(s);
        """
        # browse widgets
        for _w in widgets:
            # enable widget
            self.enable_widget(_w, True)
            # clear widget
            _w.delete(0, "end")
            # disable widget
            self.enable_widget(_w, False)
        # end for
    # end def


    def clear_listbox (self, *widgets):
        """
            clears contents for listbox widget(s);
        """
        # same as ENTRY
        self.clear_entry(*widgets)
    # end def


    def clear_text (self, *widgets):
        """
            clears contents for text widget(s);
        """
        # browse widgets
        for _w in widgets:
            # clear widget
            self.text_clear_contents(_w)
        # end for
    # end def


    def enable_widget (self, widget, state):
        """
            enables/disables a tkinter widget along with @state value;
            if @state is None, widget keeps unchanged;
        """
        # param controls
        if state is not None:
            widget.configure(
                state={True: "normal"}.get(bool(state), "disabled")
            )
        # end if
    # end def


    def get_current_selected (self, listbox):
        """
            returns dict (index, text) of current selection or None,
            otherwise;
        """
        # inits
        _sel = listbox.curselection()
        # got selected?
        if _sel:
            return dict(index=_sel[0], text=listbox.get(_sel[0]))
        else:
            return None
        # end if
    # end def


    def get_file_contents (self, fname):
        """
            returns file contents;
        """
        # inits
        fcontents = ""                                                      # FIXME
        #~ fcontents = self.text_get_contents(self.text_storyboard)
        # always return a dict
        return {fname: fcontents}
    # end def


    def init_widget (self, **kw):
        """
            hook method to be reimplemented by subclass;
        """
        # member inits
        self.mainwindow = self.winfo_toplevel()
        self.mainframe = self.mainwindow.mainframe
        self.text_clear_contents = self.mainwindow.text_clear_contents
        self.text_get_contents = self.mainwindow.text_get_contents
        self.text_set_contents = self.mainwindow.text_set_contents
        self.async = ASYNC.get_async_manager()
        # looks for ^/xml/widget/tab_storyboard.xml
        self.xml_build("tab_storyboard")
        # widget inits
        self.LBOX_SCENE = self.listbox_scene_browser
        self.LBOX_SHOT = self.listbox_shot_browser
        self.BTN_ADD = self.btn_add_shot
        self.BTN_DEL = self.btn_del_shot
        self.BTN_RENAME = self.btn_rename_shot
        self.TEXT_SCENE = self.text_scene_preview
        self.TEXT_SHOT = self.text_shot_editor
        self.ENT_SHOT = self.entry_shot_title
        self.LBL_SHOT = self.get_stringvar("lbl_shot_number")
        # update entry + buttons state
        self.slot_update_inputs()
        # event bindings
        self.bind_events(**kw)
    # end def


    def save_now (self):
        """
            ensures current template is saved before clearing;
        """
        # stop scheduled tasks
        self.async.stop(self.auto_save)
        # force task right now
        self.auto_save()
    # end def


    def setup_tab (self, fname, archive):
        """
            tab setup along @fname and @archive contents;
        """
        # set text widget contents
        #~ self.text_set_contents(self.text_storyboard, fname)
        pass
    # end def


    def slot_on_text_keypress (self, event=None, *args, **kw):
        """
            event handler: keyboard keypress for text widget;
        """
        # schedule auto-save for later
        self.async.run_after(5000, self.auto_save)
    # end def


    def slot_project_modified (self, *args, flag=True, **kw):
        """
            event handler for project's modification flag;
        """
        # reset status
        pass
    # end def


    def slot_scene_item_selected (self, event=None, *args, **kw):
        """
            event handler: listbox item has been selected;
        """
        # save previous right now!
        self.save_now()
        # update entry + buttons state
        self.slot_update_inputs()
    # end def


    def slot_shot_add (self, *args, **kw):
        """
            event handler: adding new shot to listbox;
        """
        pass                                                                # FIXME
    # end def


    def slot_shot_delete (self, *args, **kw):
        """
            event handler: deleting selected shot from listbox;
        """
        pass                                                                # FIXME
    # end def


    def slot_shot_item_selected (self, event=None, *args, **kw):
        """
            event handler: listbox item has been selected;
        """
        # save previous right now!
        self.save_now()
        # update entry + buttons state
        self.slot_update_inputs()
    # end def


    def slot_shot_rename (self, *args, **kw):
        """
            event handler: renaming current shot into listbox;
        """
        pass                                                                # FIXME
    # end def


    def slot_tab_reset (self, *args, **kw):
        """
            event handler: reset tab to new;
        """
        # reset listboxes
        self.clear_listbox(self.LBOX_SCENE, self.LBOX_SHOT)
        # reset Text widgets
        self.clear_text(self.TEXT_SCENE, self.TEXT_SHOT)
        # update entry + buttons state
        self.slot_update_inputs()
    # end def


    def slot_update_inputs (self, *args, **kw):
        """
            event handler: updates buttons state;
        """
        print("slot_update_inputs")
        # inits
        self.current_scene = self.get_current_selected(self.LBOX_SCENE)
        self.current_shot = self.get_current_selected(self.LBOX_SHOT)
        # buttons reset
        self.enable_widget(self.BTN_ADD, self.current_scene)
        self.enable_widget(self.BTN_DEL, self.LBOX_SHOT.size())
        self.enable_widget(self.BTN_RENAME, self.current_shot)
        # entry reset
        if self.current_shot:
            # enable
            self.enable_widget(self.ENT_SHOT, True)
        else:
            # clear and disable
            self.clear_entry(self.ENT_SHOT)
            # clear shot number
            self.LBL_SHOT.set("")
        # end def
    # end def


    def update_current_selected (self, listbox, text):
        """
            updates text contents of @listbox current selected item
            with @text contents;
        """
        # inits
        _sel = self.get_current_selected(listbox)
        # got selected?
        if _sel and text:
            # inits
            _index = _sel["index"]
            # delete old text
            listbox.delete(_index)
            # insert new text
            listbox.insert(_index, text)
        # end if
    # end def


    def widget_enabled (self, widget):
        """
            returns True if tkinter.Widget is enabled, False otherwise;
        """
        return bool(widget.cget("state").lower() == "normal")
    # end def

# end class ProjectTabStoryboard
