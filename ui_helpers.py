"""
ui_helpers.py
─────────────
Shared, reusable UI factory functions used by every frame and dialog.

Keeping these here means:
  • No frame/dialog repeats boilerplate widget construction.
  • A style change (e.g. button border radius) is made once and
    instantly reflected across the whole application.

All functions are pure — they create and return widgets without
knowing which frame they live inside.
"""

import customtkinter as ctk
from tkinter import ttk

from config import C, F     # Colours and fonts from the single config file


# ══════════════════════════════════════════════════════════════
# TREEVIEW FACTORY
# ══════════════════════════════════════════════════════════════
def make_treeview(parent, columns: list, col_widths: dict = None, height=15):
    """
    Build a styled ttk.Treeview inside a frame with scrollbars.

    Parameters
    ----------
    parent     : parent widget
    columns    : list of column id strings
    col_widths : dict mapping column id → pixel width (optional)
    height     : number of visible rows

    Returns the Treeview widget.
    The outer frame is packed/gridded by the caller via tree.container.
    """
    col_widths = col_widths or {}

    # Outer container that holds the tree + scrollbars
    container = ctk.CTkFrame(parent, fg_color=C['card'], corner_radius=8,
                              border_width=1, border_color=C['border'])

    # ── Global Treeview style (applied once but safe to call multiple times)
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('App.Treeview',
                    background=C['card'],
                    foreground=C['text'],
                    fieldbackground=C['card'],
                    borderwidth=0,
                    rowheight=30,
                    font=F['body'])
    style.configure('App.Treeview.Heading',
                    background=C['tree_head_bg'],
                    foreground=C['text'],
                    font=F['subhead'],
                    relief='flat')
    style.map('App.Treeview',
              background=[('selected', C['tree_sel'])],
              foreground=[('selected', C['text'])])

    # ── Treeview widget
    tree = ttk.Treeview(container, columns=columns, show='headings',
                        style='App.Treeview', height=height, selectmode='browse')

    # ── Column headers and widths
    for col in columns:
        w = col_widths.get(col, 120)
        tree.heading(col, text=col.replace('_', ' ').title())
        tree.column(col, width=w, minwidth=60, anchor='w')

    # ── Scrollbars
    vsb = ttk.Scrollbar(container, orient='vertical',   command=tree.yview)
    hsb = ttk.Scrollbar(container, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    # ── Layout inside container (grid is ideal for scrollbars)
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid( row=0, column=1, sticky='ns')
    hsb.grid( row=1, column=0, sticky='ew')
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    # Attach container reference so caller can pack/grid it
    tree.container = container

    # Alternate row colours for readability
    tree.tag_configure('odd',  background=C['card'])
    tree.tag_configure('even', background=C['tree_alt'])
    tree.tag_configure('warn', background='#FFF3CD', foreground='#856404')

    return tree


# ══════════════════════════════════════════════════════════════
# TREEVIEW DATA HELPER
# ══════════════════════════════════════════════════════════════
def populate_tree(tree, rows: list, keys: list):
    """
    Clear and refill a Treeview.

    Parameters
    ----------
    tree : ttk.Treeview
    rows : list of dicts returned from DatabaseManager
    keys : ordered list of dict keys matching treeview columns
    """
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        values = [row.get(k, '') for k in keys]
        tag = 'even' if i % 2 == 0 else 'odd'
        # Highlight overdue book issues
        if row.get('overdue') == 'YES':
            tag = 'warn'
        tree.insert('', 'end', values=values, tags=(tag,))


# ══════════════════════════════════════════════════════════════
# WIDGET SHORTHAND FACTORIES
# ══════════════════════════════════════════════════════════════
def lbl(parent, text, font=None, color=None, **kw):
    """Shorthand for a styled CTkLabel."""
    return ctk.CTkLabel(parent, text=text,
                        font=font or F['body'],
                        text_color=color or C['text'], **kw)


def entry(parent, placeholder='', width=220, **kw):
    """Shorthand for a styled CTkEntry."""
    return ctk.CTkEntry(parent, placeholder_text=placeholder,
                        width=width, height=36,
                        corner_radius=8,
                        border_color=C['border'],
                        fg_color=C['card'],
                        text_color=C['text'],
                        placeholder_text_color=C['text2'], **kw)


def btn(parent, text, command, color=None, hover=None, width=110, **kw):
    """Shorthand for a styled CTkButton."""
    return ctk.CTkButton(parent, text=text, command=command,
                         width=width, height=36,
                         corner_radius=8,
                         font=F['btn'],
                         fg_color=color or C['accent'],
                         hover_color=hover or C['accent_h'],
                         text_color=C['white'], **kw)


# ══════════════════════════════════════════════════════════════
# LAYOUT HELPERS
# ══════════════════════════════════════════════════════════════
def section_header(parent, title: str, subtitle: str = ''):
    """Render a page title + optional subtitle label."""
    lbl(parent, title, font=F['title'], color=C['text']).pack(anchor='w')
    if subtitle:
        lbl(parent, subtitle, font=F['body'], color=C['text2']).pack(anchor='w', pady=(2, 0))


def divider(parent):
    """Thin horizontal rule between sections."""
    ctk.CTkFrame(parent, height=1, fg_color=C['border']).pack(fill='x', pady=10)