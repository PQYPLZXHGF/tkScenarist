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
from datetime import timedelta, date
import json
import tkinter.messagebox as MB
import tkinter.simpledialog as SD
import tkRAD.widgets.rad_canvas as RC


class ResourcesCanvas (RC.RADCanvas):
    """
        Resources planning canvas class;
    """

    # class constant defs
    CONFIG = {
        "background": "grey80",
        "height": None,
        "highlightbackground": "grey20",
        "highlightthickness": 1,
        "takefocus": 0,
        "width": 0,
    } # end of CONFIG


    def bbox_add (self, bbox1, bbox2):
        """
            returns coordinates sum of bounding boxes;
        """
        return tuple(map(lambda x: sum(x), zip(bbox1, bbox2)))
    # end def


    def box_rel (self, (x0, y0), (width, height)):
        """
            returns box coordinates relative to (x0, y0) point of
            origin and to (width, height);
        """
        return (x0, y0, x0 + width, y0 + height)
    # end def


    def bind_events (self, **kw):
        """
            event bindings;
        """
        # app-wide event bindings
        #~ self.events.connect_dict(
            #~ {
                #~ "Project:Modified": self.slot_project_modified,
            #~ }
        #~ )
        # tkinter event bindings
        self.bind("<Configure>", self.update_canvas)
        self.bind("<Button-1>", self.slot_start_drag)
        self.bind("<Motion>", self.slot_drag_pending)
        self.bind("<ButtonRelease-1>", self.slot_drop)
        self.bind("<Control-ButtonRelease-1>", self.slot_remove_item)
        self.bind("<Double-Button-1>", self.slot_double_clicked)
    # end def


    def center_x (self):
        """
            returns x coordinates for canvas' center point;
        """
        # return center point x coordinates
        return self.winfo_reqwidth() // 2
    # end def


    def center_xy (self):
        """
            returns (x, y) coordinates for canvas' center point;
        """
        # return center point coordinates
        return (self.center_x(), self.center_y())
    # end def


    def center_y (self):
        """
            returns y coordinates for canvas' center point;
        """
        # return center point y coordinates
        return self.winfo_reqheight() // 2
    # end def


    def clear_canvas (self, *args, **kw):
        """
            event handler for clearing up canvas;
        """
        # clear canvas
        self.delete("all")
        self.configure(scrollregion=(0, 0, 0, 0))
        self.xview_moveto(0)
        self.yview_moveto(0)
    # end def


    def dnd_reset (self, *args, **kw):
        """
            event handler for resetting D'n'D feature;
        """
        # inits
        self.drag_mode = 0
        self.drag_tag = ""
        self.drag_start_xy = (0, 0)
        self.drag_last_pos = (0, 0)
        self.auto_scroll = False
    # end def


    def get_bbox_center (self, tag):
        """
            returns (x, y) coordinates of central point for a bbox
            identified by group tag;
        """
        # inits
        _bbox = self.bbox(tag)
        # got bbox?
        if _bbox:
            # get coords
            x1, y1, x2, y2 = _bbox
            # return center xy
            return ((x1 + x2) // 2, (y1 + y2) // 2)
        # end if
    # end def


    def get_file_contents (self):
        """
            returns file contents as string of chars;
        """
        # inits
        _dict = dict()
        pass                                                                # FIXME
        return json.dumps(_dict)
    # end def


    def get_new_tag (self, tag_radix=None):
        """
            returns a new canvas tag name indexed with
            self.instance_counter;
        """
        # inits
        tag_radix = tag_radix or "group"
        # update counter
        self.instance_counter += 1
        # return new tag name
        return "{}#{}".format(tag_radix, self.instance_counter)
    # end def


    def get_real_pos (self, x, y):
        """
            returns real position coordinates for canvas viewport
            coordinates;
        """
        return (int(self.canvasx(x)), int(self.canvasy(y)))
    # end def


    def get_segment_center (self, start_xy, end_xy):
        """
            returns (x, y) coordinates of central point for a segment;
        """
        # inits
        x0, y0 = start_xy
        x1, y1 = end_xy
        # calculate
        return ((x0 + x1) // 2, (y0 + y1) // 2)
    # end def


    def group_add (self, name, **kw):
        """
            adds a new canvas group;
        """
        # param controls
        if name:
            # already exists?
            if name in self.canvas_groups:
                raise KeyError(
                    _("canvas group name '{gname}' already exists.")
                    .format(gname=name)
                )
            # new to list
            else:
                # add new group
                self.canvas_groups[name] = kw
                # return group
                return kw
            # end if
        # end if
        # failed
        return None
    # end def


    def init_members (self, **kw):
        """
            class members only inits;
        """
        # members only inits
        self.instance_counter = 0
        self.canvas_groups = dict()
        # drag'n'drop feature
        self.dnd_reset()
        # date ruler feature
        self.date_ruler.reset()
        # item feature
        self.item_list.reset()
    # end def


    def init_widget (self, **kw):
        """
            virtual method to be implemented in subclass;
        """
        # date ruler inits
        self.date_ruler = RCDateRuler(self)
        # item list inits
        self.item_list = RCItemList(self)
        # member inits
        self.init_members(**kw)
        # event bindings
        self.bind_events()
    # end def


    def reset (self, *args, **kw):
        """
            resets canvas to new;
        """
        # clear canvas
        self.clear_canvas()
        # reset members
        self.init_members(**kw)
    # end def


    def size_xy (self):
        """
            returns (width, height) coordinates;
        """
        # get coordinates
        return (self.winfo_reqwidth(), self.winfo_reqheight())
    # end def


    def slot_double_clicked (self, event=None, *args, **kw):
        """
            event handler: mouse double-clicked;
        """
        print("slot_double_clicked")
        # param controls
        if event:
            # inits
            x, y = self.get_real_pos(event.x, event.y)
            pass                                                            # FIXME
        # end if
    # end def


    def slot_drag_pending (self, event=None, *args, **kw):
        """
            event handler: pending D'n'D on mouse motion;
        """
        #~ print("slot_drag_pending")
        # param controls
        if event:
            # dragging something?
            if self.drag_mode:
                # inits
                x, y = self.get_real_pos(event.x, event.y)
                x0, y0 = self.drag_last_pos
                dx, dy = (x - x0), (y - y0)
                # update pos
                self.drag_last_pos = (x, y)
                pass                                                            # FIXME
                # update canvas
                self.update_canvas()
                # scrolling
                self.scan_dragto(event.x, event.y, gain=-1)
            # auto-scrolling mode?
            elif self.auto_scroll:
                # scrolling
                self.scan_dragto(event.x, event.y, gain=-5)
            # end if
        # end if
    # end def


    def slot_drop (self, event=None, *args, **kw):
        """
            event handler: D'n'D dropping on mouse release;
        """
        print("slot_drop")
        # param controls
        if event and self.drag_mode:
            # inits
            x, y = self.get_real_pos(event.x, event.y)
            pass                                                            # FIXME
        # end if
        # reset D'n'D mode
        self.dnd_reset()
        # update canvas
        self.update_canvas()
    # end def


    def slot_remove_item (self, event=None, *args, **kw):
        """
            event handler: mouse Ctrl+Click;
        """
        print("slot_remove_item")
        # param controls
        if event:
            # inits
            x, y = self.get_real_pos(event.x, event.y)
            pass                                                            # FIXME
        # end if
        # reset D'n'D mode
        self.dnd_reset()
        # update canvas
        self.update_canvas()
    # end def


    def slot_start_drag (self, event=None, *args, **kw):
        """
            event handler: mouse Drag-and-drop feature;
        """
        print("slot_start_drag")
        # inits
        self.dnd_reset()
        # got mouse event?
        if event:
            # automatic scrolling feature
            self.scan_mark(event.x, event.y)
            # inits
            x, y = self.get_real_pos(event.x, event.y)
            pass                                                            # FIXME
        # end if
    # end def


    def update_canvas (self, *args, **kw):
        """
            event handler for canvas contents updating;
        """
        print("update_canvas")
        # inits
        _bbox = self.bbox("all")
        # got items?
        if _bbox:
            print("bbox:", _bbox)
            # get all contents bbox
            x0, y0, x1, y1 = _bbox
            _cw, _ch = self.size_xy()
            x0, y0 = (min(0, x0 + 1), min(0, y0 + 1))
            #~ x1, y1 = (max(x1 - 1, _cw), max(y1 - 1, _ch))
            # reset scroll region size
            self.configure(scrollregion=(x0, y0, x1, y1))
            print("scrollregion:", self.cget("scrollregion"))
            # project has been modified
            #~ self.events.raise_event("Project:Modified")
        # no items
        else:
            # better clean up everything
            self.reset()
        # end if
    # end def


    def viewport_center_xy (self):
        """
            returns (x, y) real canvas coordinates of viewport's center
            point;
        """
        # inits
        x, y = self.center_xy()
        # viewport's center point
        return (int(self.canvasx(x)), int(self.canvasy(y)))
    # end def

# end class ResourcesCanvas



class RCDateRuler:
    """
        Resources Canvas Date Ruler component class;
    """

    # class constant defs
    XY_ORIGIN = (0, 0)


    def __init__ (self, canvas, **kw):
        """
            class constructor;
        """
        # member inits
        self.canvas = canvas
        self.date_min = kw.get("date_min") or date.today()
        self.date_max = (
            kw.get("date_max") or
            self.date_min + timedelta(days=7)
        )
        self.tag = (
            kw.get("tag") or
            "{}#{}".format(self.__class__.__name__, id(self))
        )
    # end def


    def reset (self, *args, **kw):
        """
            redraws component on canvas;
        """
        # ensure no more previous
        self.canvas.delete(self.tag)
        # redraw frame
        self.frame_id = self.canvas.create_rectangle(
            self.canvas.box_rel(self.XY_ORIGIN, 200, 30),
            outline="black",
            fill="grey90",
            width=1,
            tags=self.tag,
        )
    # end def

# end class RCDateRuler



class RCItemList:
    """
        Resources Canvas Item List component class;
    """

    # class constant defs
    XY_ORIGIN = (0, 30)


    def __init__ (self, canvas, **kw):
        """
            class constructor;
        """
        # member inits
        self.canvas = canvas
        self.items = kw.get("items") or list()
        self.tag = (
            kw.get("tag") or
            "{}#{}".format(self.__class__.__name__, id(self))
        )
    # end def


    def reset (self, *args, **kw):
        """
            redraws component on canvas;
        """
        # ensure no more previous
        self.canvas.delete(self.tag)
        # redraw frame
        self.frame_id = self.canvas.create_rectangle(
            self.canvas.box_rel(self.XY_ORIGIN, 200, 300),
            outline="black",
            fill="grey90",
            width=1,
            tags=self.tag,
        )
    # end def

# end class RCItemList