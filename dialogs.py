"""
dialogs.py
──────────
ModalDialog — the base class for every Add / Edit popup in the app.

Concrete dialog subclasses (MemberDialog, BookDialog, etc.) each live
alongside the frame they belong to, inside the frames/ package.
Only the shared base lives here so there are no circular imports.

Inheritance chain for every popup:
    ctk.CTkToplevel
        └── ModalDialog          ← defined here
                └── MemberDialog / BookDialog / ...  ← defined in frames/
"""

import customtkinter as ctk

from config     import C, F
from ui_helpers import lbl, btn


# ══════════════════════════════════════════════════════════════
# MODAL DIALOG BASE
# ══════════════════════════════════════════════════════════════
class ModalDialog(ctk.CTkToplevel):
    """
    A centred, styled popup window.
    Subclasses override build_form() and on_save().
    """

    def __init__(self, parent, title: str, width=520, height=460):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.configure(fg_color=C['bg'])

        # ── Centre on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - width)  // 2
        y  = (sh - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # ── Make this window modal (blocks parent interaction)
        self.grab_set()
        self.focus_set()

        self._build_chrome(title)
        self.build_form()
        self._build_footer()

    def _build_chrome(self, title):
        """Render the dialog header bar."""
        hdr = ctk.CTkFrame(self, fg_color=C['accent'], corner_radius=0, height=52)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        lbl(hdr, title, font=F['heading'], color=C['white']).pack(
            side='left', padx=18, pady=12)

        # Body scroll frame
        self.body = ctk.CTkScrollableFrame(self, fg_color=C['bg'])
        self.body.pack(fill='both', expand=True, padx=20, pady=10)

    def _build_footer(self):
        """Cancel / Save button row at the bottom."""
        foot = ctk.CTkFrame(self, fg_color=C['card'],
                            corner_radius=0, height=56,
                            border_width=1, border_color=C['border'])
        foot.pack(fill='x', side='bottom')
        foot.pack_propagate(False)

        btn(foot, '✕  Cancel', self.destroy,
            color='#6C757D', hover='#5A6268', width=120
            ).pack(side='right', padx=(8, 16), pady=10)
        btn(foot, '✔  Save',   self.on_save,
            width=120
            ).pack(side='right', padx=4, pady=10)

    def form_row(self, label_text: str, widget):
        """
        Helper to add a label + widget pair inside the form body.
        Uses pack layout with consistent spacing.
        """
        row = ctk.CTkFrame(self.body, fg_color='transparent')
        row.pack(fill='x', pady=5)
        lbl(row, label_text, font=F['subhead'], color=C['text2']).pack(anchor='w')
        widget.pack(fill='x', pady=(2, 0))
        return widget

    def build_form(self):
        """Override in subclass to add form fields."""
        pass

    def on_save(self):
        """Override in subclass to handle form submission."""
        pass