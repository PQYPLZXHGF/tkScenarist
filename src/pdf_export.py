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
import os.path
import datetime

from reportlab.platypus import SimpleDocTemplate, Frame
from reportlab.platypus import Paragraph, Spacer, PageBreak
from reportlab.platypus.frames import ShowBoundaryValue
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.enums import *                   # text alignments

import tkRAD.core.path as P
import tkRAD.core.services as SM
from tkRAD.core import tools


def build_document (doc):
    """
        builds final doc for specific PDF document;
    """
    # delegate to specific
    doc.build_document()
    # progression status (0-100%)
    return doc.progress
# end def


def build_elements (doc):
    """
        builds elements for specific PDF document;
    """
    # delegate to specific
    doc.build_elements()
    # progression status (0-100%)
    return doc.progress
# end def


def gather_informations (doc):
    """
        gathers informations for specific PDF document;
    """
    # delegate to specific
    doc.gather_info()
    # progression status (0-100%)
    return doc.progress
# end def


def get_pdf_document (doc_name, **kw):
    """
        returns a new instance for an app-specific PDF document with
        filepath built along with @doc_name document name value;
    """
    # new document instance
    return eval(
        "PDFDocument{name}(doc_name, **kw)"
        .format(name=str(doc_name).title().replace("_", ""))
    )
# end def


def get_stylesheet ():
    """
        returns a dict of ParagraphStyle settings;
    """
    return {
        # main styles
        "header": ParagraphStyle(
            "header",
            fontName="Times",
            fontSize=12,
            leading=0,
            alignment=TA_CENTER,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Times-Italic",
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "footer_tiny": ParagraphStyle(
            "footer_tiny",
            fontName="Helvetica-Oblique",
            fontSize=6,
            leading=6,
            alignment=TA_CENTER,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "body": ParagraphStyle(
            "body",
            alignment=TA_JUSTIFY,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=0,
            spaceAfter=0.1*inch,
        ),

        # project data styles

        "title": ParagraphStyle(
            "title",
            fontName="Times-Bold",
            fontSize=36,
            leading=40,
            alignment=TA_CENTER,
            leftIndent=0.5*inch,
            rightIndent=0.5*inch,
            spaceBefore=0,
            spaceAfter=0.1*inch,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Times-Italic",
            fontSize=18,
            leading=20,
            alignment=TA_CENTER,
            leftIndent=1*inch,
            rightIndent=1*inch,
            spaceBefore=0,
            spaceAfter=0.1*inch,
        ),
        "episode": ParagraphStyle(
            "episode",
            fontName="Helvetica",
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
            leftIndent=1.5*inch,
            rightIndent=1.5*inch,
            spaceBefore=0,
            spaceAfter=0.1*inch,
        ),
        "author": ParagraphStyle(
            "author",
            fontName="Times-BoldItalic",
            fontSize=16,
            leading=18,
            alignment=TA_CENTER,
            leftIndent=1*inch,
            rightIndent=1*inch,
            spaceBefore=0.3*inch,
            spaceAfter=0.1*inch,
        ),
        "contact": ParagraphStyle(
            "contact",
            fontName="Times-Italic",
            fontSize=12,
            leading=12,
            alignment=TA_LEFT,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=0,
            spaceAfter=6,
        ),

        # scenario tab styles

        "action": ParagraphStyle(
            "action",
            fontName="Times",
            fontSize=12,
            leading=0,
            alignment=TA_CENTER,
        ),
        "character": ParagraphStyle(
            "character",
            fontName="Times",
            fontSize=12,
            leading=0,
            alignment=TA_CENTER,
        ),
        "dialogue": ParagraphStyle(
            "dialogue",
            fontName="Times",
            fontSize=12,
            leading=0,
            alignment=TA_CENTER,
        ),
        "parenthetical": ParagraphStyle(
            "parenthetical",
            fontName="Times",
            fontSize=12,
            leading=0,
            alignment=TA_CENTER,
        ),
        "scene": ParagraphStyle(
            "scene",
            fontName="Times",
            fontSize=12,
            leading=0,
            alignment=TA_CENTER,
        ),
        "transition": ParagraphStyle(
            "transition",
            fontName="Times",
            fontSize=12,
            leading=0,
            alignment=TA_CENTER,
        ),

        # storyboard tab styles

        "shot_title": ParagraphStyle(
            "shot_title",
            fontName="Times",
            fontSize=12,
            leading=0,
            alignment=TA_CENTER,
        ),
        "shot_body": ParagraphStyle(
            "shot_body",
            fontName="Times",
            fontSize=12,
            leading=0,
            alignment=TA_CENTER,
        ),
    }
# end def



class PDFDocumentBase:
    """
        Base class for tkScenarist specific PDF documents to export;
    """

    def __init__ (self, doc_name, **kw):
        """
            class constructor;
        """
        # member inits
        self.doc_name = doc_name
        self.options = kw.get("options")
        self.project_data = kw.get("data")
        self.app = SM.ask_for("app") # application
        self.pfm = SM.ask_for("PFM") # Project File Management
        self.mainwindow = self.app.mainwindow
        self.mainframe = self.mainwindow.mainframe
        self.database = self.mainwindow.database
        self.document = self.get_pdf_document(doc_name)
        self.styles = get_stylesheet()
        self.elements = list()
        self.progress = 0
        self.index = 0
    # end def


    def add_pagebreak (self):
        """
            adds a PageBreak() object to elements;
        """
        # inits
        self.elements.append(PageBreak())
    # end def


    def add_paragraph (self, text, style):
        """
            adds a Paragraph() object only if @text is a plain string
            of chars;
        """
        # ensure we have some text
        if tools.is_pstr(text):
            # add paragraph
            self.elements.append(Paragraph(text, style))
        # end if
    # end def


    def build_document (self):
        """
            hook method to be reimplemented in subclass;
            builds final PDF document;
        """
        print("build_document")
        print("elements:", bool(self.elements))
        # reset progress
        self.reset_progress()
        # must do it in one shot
        self.document.build(
            self.elements,
            onFirstPage=self.draw_first_page,
            onLaterPages=self.draw_pages,
        )
        # procedure is complete
        self.progress = 100
    # end def


    def build_elements (self):
        """
            hook method to be reimplemented in subclass;
            builds document internal elements;
        """
        print("build_elements")
        # inits
        _styles = self.styles
        # reset progress
        self.reset_progress()
        # first page elements
        self.set_first_page_elements()
        # put your own code in subclass
        for i in range(20):
            # dummy text
            self.add_paragraph("*** TEST ***", _styles["body"])
        # end if
        # procedure is complete
        self.progress = 100
    # end def


    def draw_first_page (self, canvas, doc):
        """
            hook method to be reimplemented in subclass;
            draws fix elements (header, footer, etc) on page;
        """
        print("draw_first_page")
        # save settings
        canvas.saveState()
        # inits
        _data = self.project_data
        _styles = self.styles
        _width, _height = doc.pagesize
        # doc inner margin width and height
        _margin_w = _width - doc.leftMargin - doc.rightMargin
        # set header
        _frame_h = _styles["header"].fontSize + 4
        _frame = Frame(
            doc.leftMargin, _height - 0.75 * doc.topMargin,
            _margin_w, _frame_h,
            leftPadding=0, rightPadding=0,
            topPadding=0, bottomPadding=0,
            showBoundary=0,
        )
        _frame.addFromList(
            [Paragraph(self.fancy_name, _styles["header"])],
            canvas
        )
        # set contact frame
        _style = _styles["contact"]
        _frame_h = _style.fontSize + _style.spaceAfter
        _frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            _margin_w, _frame_h * 4 - _style.spaceAfter,
            showBoundary=ShowBoundaryValue(),
        )
        _frame.addFromList(
            [
                Paragraph(_(_t).format(**_data), _style)
                for _t in (
                    "Contact: {project_author}",
                    "E-mail: {project_author_email}",
                    "Phone: {project_author_phone}",
                )
            ],
            canvas
        )
        # set footer + mentions
        _frame_h = (
            _styles["footer"].fontSize
            + _styles["footer_tiny"].fontSize + 8
        )
        _frame = Frame(
            doc.leftMargin, 0.5 * doc.bottomMargin,
            _margin_w, _frame_h,
            leftPadding=0, rightPadding=0,
            topPadding=0, bottomPadding=0,
            showBoundary=0,
        )
        _frame.addFromList(
            [
                Paragraph(
                    _("Printed on {}")
                    .format(datetime.datetime.today().strftime("%c")),
                    _styles["footer"]
                ),
                Paragraph(
                    _(
                        "Document generated by {name} with "
                        "{pdflib} PDF toolkit"
                    ).format(**self.app.APP),
                    _styles["footer_tiny"]
                ),
            ],
            canvas
        )
        # restore settings
        canvas.restoreState()
    # end def


    def draw_pages (self, canvas, doc):
        """
            hook method to be reimplemented in subclass;
            draws fix elements (header, footer, etc) on page;
        """
        print("draw_pages")
        # put your own code in subclass
        pass
        # save settings
        canvas.saveState()
        # set header
        pass # project title - episode
        # set footer
        pass # page number (centered)
        # restore settings
        canvas.restoreState()
    # end def


    @property
    def fancy_name (self):
        """
            property attribute;
            returns a fancier name for self.doc_name;
            this is a READ-ONLY property;
        """
        return _(str(self.doc_name).title().replace("_", "/"))
    # end def


    def gather_info (self):
        """
            hook method to be reimplemented in subclass;
            gathers specific informations for document building;
        """
        print("gather_info")
        # reset progress
        self.reset_progress()
        # put your own code in subclass
        pass
        # procedure is complete
        self.progress = 100
    # end def


    def get_pdf_document (self, doc_name):
        """
            provides a reportlab.PDFDocument;
        """
        print("get_pdf_document")
        # param controls
        if tools.is_pstr(doc_name):
            # inits
            _data = self.project_data
            _fpath, _fext = os.path.splitext(self.pfm.project_path)
            # rebuild filepath
            _fpath = P.normalize("{}-{}.pdf".format(_fpath, doc_name))
            # PDF document instance
            return SimpleDocTemplate(
                filename=_fpath,
                author=_data.get("project_author"),
                title="{project_title} - "
                "{project_subtitle} - "
                "{project_episode}"
                .format(**_data),
                subject=self.fancy_name,
                creator=self.app.APP.get("title"),
            )
        # error
        else:
            # notify
            raise ValueError(
                "parameter 'doc_name' must be of "
                "plain string type."
            )
        # end if
    # end def


    @property
    def progress (self):
        """
            property attribute;
            progression status (0.0-100.0%);
        """
        return self.__progress
    # end def

    @progress.setter
    def progress (self, value):
        # inits
        self.__progress = float(min(100, max(0, value)))
    # end def

    @progress.deleter
    def progress (self):
        # delete
        del self.__progress
    # end def


    def reset_progress (self):
        """
            resets progress status to 0 if >= 100 (%);
        """
        print("reset_progress")
        if self.progress >= 100:
            self.progress = 0
        # end if
    # end def


    def set_first_page_elements (self):
        """
            sets document's first page flowable elements such as title,
            subtitle, episode, etc;
        """
        # inits
        _data = self.project_data
        _styles = self.styles
        # reset elements
        self.elements.clear()
        # add spacer
        self.elements.append(Spacer(0, 2*inch))
        # add paragraphs
        self.add_paragraph(
            _data.get("project_title"), _styles["title"]
        )
        self.add_paragraph(
            _data.get("project_subtitle"), _styles["subtitle"]
        )
        self.add_paragraph(
            _data.get("project_episode"), _styles["episode"]
        )
        self.add_paragraph(
            tools.str_complete(
                _("By {}"),
                _data.get("project_author")
            ),
            _styles["author"]
        )
        # add page break
        self.add_pagebreak()
    # end def

# end class PDFDocumentBase



class PDFDocumentCharacters (PDFDocumentBase):
    """
        specific PDF document class for Characters application tab;
    """
    pass
# end class PDFDocumentCharacters



class PDFDocumentDraftNotes (PDFDocumentBase):
    """
        specific PDF document class for Draft/Notes application tab;
    """
    pass
# end class PDFDocumentDraftNotes



class PDFDocumentPitchConcept (PDFDocumentBase):
    """
        specific PDF document class for Pitch/Concept application tab;
    """
    pass
# end class PDFDocumentPitchConcept



class PDFDocumentResources (PDFDocumentBase):
    """
        specific PDF document class for Resources application tab;
    """
    pass
# end class PDFDocumentResources



class PDFDocumentScenario (PDFDocumentBase):
    """
        specific PDF document class for Scenario application tab;
    """
    pass
# end class PDFDocumentScenario



class PDFDocumentStoryboard (PDFDocumentBase):
    """
        specific PDF document class for Storyboard application tab;
    """
    pass
# end class PDFDocumentStoryboard
