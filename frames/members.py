"""
frames/members.py
─────────────────
MembersFrame  — full CRUD grid for the Members table.
MemberDialog  — Add / Edit popup for a single member record.

Both classes are co-located because the dialog is only ever
opened from within the frame; keeping them together avoids
an extra import file for a tightly coupled pair.
"""

import customtkinter as ctk
from tkinter import messagebox

from config     import C, F
from ui_helpers import lbl, btn, entry, make_treeview, populate_tree, section_header, divider
from dialogs    import ModalDialog


# ══════════════════════════════════════════════════════════════
# MEMBERS FRAME
# ══════════════════════════════════════════════════════════════
class MembersFrame(ctk.CTkFrame):
    """CRUD interface for the Members table."""

    COLS   = ['member_id', 'name', 'email', 'phone', 'department', 'join_date']
    WIDTHS = {'member_id': 60, 'name': 160, 'email': 200,
              'phone': 110, 'department': 120, 'join_date': 110}

    def __init__(self, parent, db, **kw):
        super().__init__(parent, fg_color=C['bg'], **kw)
        self.db = db
        self._build()

    def _build(self):
        # ── Page header
        hdr = ctk.CTkFrame(self, fg_color='transparent')
        hdr.pack(fill='x', padx=24, pady=(20, 8))
        section_header(hdr, '👥  Members', 'Manage employees / library members')

        divider(self)

        # ── Search bar + action buttons
        toolbar = ctk.CTkFrame(self, fg_color='transparent')
        toolbar.pack(fill='x', padx=24, pady=(0, 12))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add('write', lambda *_: self.refresh())
        e = ctk.CTkEntry(toolbar, textvariable=self.search_var,
                         placeholder_text='🔍  Search by name, email or department …',
                         width=320, height=36, corner_radius=8,
                         border_color=C['border'], fg_color=C['card'],
                         text_color=C['text'], placeholder_text_color=C['text2'])
        e.pack(side='left')

        btn(toolbar, '＋  Add Member', self._add,    width=140).pack(side='right', padx=(8, 0))
        btn(toolbar, '✎  Edit',        self._edit,
            color='#6C757D', hover='#5A6268', width=100).pack(side='right', padx=4)
        btn(toolbar, '🗑  Delete',      self._delete,
            color=C['danger'], hover='#C0392B', width=100).pack(side='right')

        # ── Treeview
        self.tree = make_treeview(self, self.COLS, self.WIDTHS, height=20)
        self.tree.container.pack(fill='both', expand=True, padx=24, pady=(0, 20))

        self.refresh()

    def refresh(self):
        rows = self.db.get_members(self.search_var.get())
        populate_tree(self.tree, rows, self.COLS)

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a row first.")
            return None
        return self.tree.item(sel[0])['values'][0]

    def _add(self):
        MemberDialog(self, self.db, callback=self.refresh)

    def _edit(self):
        mid = self._selected_id()
        if mid is None:
            return
        vals = self.tree.item(self.tree.selection()[0])['values']
        MemberDialog(self, self.db, callback=self.refresh,
                     prefill={'id': mid, 'name': vals[1], 'email': vals[2],
                              'phone': vals[3], 'department': vals[4]})

    def _delete(self):
        mid = self._selected_id()
        if mid is None:
            return
        if messagebox.askyesno("Confirm Delete",
                               "Delete this member?\n\nAll associated book issues "
                               "and asset assignments will also be removed."):
            self.db.delete_member(mid)
            self.refresh()


# ══════════════════════════════════════════════════════════════
# MEMBER DIALOG  (Add / Edit)
# ══════════════════════════════════════════════════════════════
class MemberDialog(ModalDialog):
    def __init__(self, parent, db, callback, prefill=None):
        self.db       = db
        self.callback = callback
        self.prefill  = prefill or {}
        title = 'Edit Member' if prefill else 'Add New Member'
        super().__init__(parent, title, width=480, height=420)

    def build_form(self):
        p = self.prefill
        self.e_name  = self.form_row('Full Name *', entry(self.body, 'Enter full name'))
        self.e_email = self.form_row('Email',        entry(self.body, 'Enter email address'))
        self.e_phone = self.form_row('Phone',        entry(self.body, 'Enter phone number'))
        self.e_dept  = self.form_row('Department',   entry(self.body, 'e.g. Engineering'))

        # Pre-fill when editing
        if p:
            self.e_name.insert(0,  p.get('name',       ''))
            self.e_email.insert(0, p.get('email',      ''))
            self.e_phone.insert(0, p.get('phone',      ''))
            self.e_dept.insert(0,  p.get('department', ''))

    def on_save(self):
        name  = self.e_name.get().strip()
        email = self.e_email.get().strip()
        phone = self.e_phone.get().strip()
        dept  = self.e_dept.get().strip()
        if not name:
            messagebox.showwarning("Required", "Full Name is required.", parent=self)
            return
        if self.prefill:
            self.db.update_member(self.prefill['id'], name, email, phone, dept)
        else:
            self.db.add_member(name, email, phone, dept)
        self.callback()
        self.destroy()