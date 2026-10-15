"""
frames/assets.py
────────────────
AssetFrame        — two-tab view: Assets inventory + Assignments tracking.
AssetDialog       — Add / Edit popup for a single asset record.
AssignAssetDialog — Transaction popup to assign an asset to a member.

All three are co-located because the dialogs are only ever
opened from within AssetFrame.
"""

import datetime
import customtkinter as ctk
from tkinter import messagebox

from config     import C, F
from ui_helpers import lbl, btn, entry, make_treeview, populate_tree, section_header, divider
from dialogs    import ModalDialog


# ══════════════════════════════════════════════════════════════
# ASSET FRAME
# ══════════════════════════════════════════════════════════════
class AssetFrame(ctk.CTkFrame):
    """Asset Management — company inventory + assignment tracking."""

    def __init__(self, parent, db, **kw):
        super().__init__(parent, fg_color=C['bg'], **kw)
        self.db = db
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color='transparent')
        hdr.pack(fill='x', padx=24, pady=(20, 8))
        section_header(hdr, '💼  Asset Management',
                       'Track company hardware, software and assignments')
        divider(self)

        tabs = ctk.CTkTabview(self, fg_color=C['bg'],
                              segmented_button_fg_color=C['border'],
                              segmented_button_selected_color=C['accent'],
                              segmented_button_selected_hover_color=C['accent'],
                              segmented_button_unselected_color='#6C757D',
                              segmented_button_unselected_hover_color='#6C757D',
                              text_color=C['white'],
                              text_color_disabled=C['text'])
        tabs.pack(fill='both', expand=True, padx=16, pady=(0, 16))
        tabs.add('🖥  Assets')
        tabs.add('📋  Assignments')

        self._build_assets_tab(tabs.tab('🖥  Assets'))
        self._build_assignments_tab(tabs.tab('📋  Assignments'))

    # ── ASSETS TAB ────────────────────────────────────────────
    def _build_assets_tab(self, parent):
        parent.configure(fg_color=C['bg'])
        tb = ctk.CTkFrame(parent, fg_color='transparent')
        tb.pack(fill='x', pady=(8, 10))

        self.asset_search = ctk.StringVar()
        self.asset_search.trace_add('write', lambda *_: self._refresh_assets())
        ctk.CTkEntry(tb, textvariable=self.asset_search,
                     placeholder_text='🔍  Search name, type or serial …',
                     width=300, height=36, corner_radius=8,
                     border_color=C['border'], fg_color=C['card'],
                     text_color=C['text'],
                     placeholder_text_color=C['text2']).pack(side='left')

        btn(tb, '＋  Add Asset',  self._add_asset,    width=130).pack(side='right', padx=(6, 0))
        btn(tb, '✎  Edit',       self._edit_asset,
            color='#6C757D', hover='#5A6268', width=90).pack(side='right', padx=4)
        btn(tb, '🗑  Delete',    self._delete_asset,
            color=C['danger'], hover='#C0392B', width=90).pack(side='right')

        cols   = ['asset_id', 'asset_name', 'asset_type', 'brand', 'model',
                  'serial_number', 'condition', 'status', 'purchase_date']
        widths = {'asset_id': 60, 'asset_name': 180, 'asset_type': 110,
                  'brand': 90, 'model': 130, 'serial_number': 130,
                  'condition': 80, 'status': 100, 'purchase_date': 110}
        self.asset_tree = make_treeview(parent, cols, widths, height=18)
        self.asset_tree.container.pack(fill='both', expand=True)
        self._refresh_assets()

    def _refresh_assets(self):
        rows = self.db.get_assets(self.asset_search.get())
        populate_tree(self.asset_tree, rows,
                      ['asset_id', 'asset_name', 'asset_type', 'brand', 'model',
                       'serial_number', 'condition', 'status', 'purchase_date'])

    def _selected_asset_id(self):
        sel = self.asset_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return None
        return self.asset_tree.item(sel[0])['values'][0]

    def _add_asset(self):
        AssetDialog(self, self.db, callback=self._refresh_assets)

    def _edit_asset(self):
        aid = self._selected_asset_id()
        if aid is None:
            return
        vals = self.asset_tree.item(self.asset_tree.selection()[0])['values']
        AssetDialog(self, self.db, callback=self._refresh_assets,
                    prefill={'id': aid, 'asset_name': vals[1], 'asset_type': vals[2],
                             'brand': vals[3], 'model': vals[4], 'serial_number': vals[5],
                             'condition': vals[6], 'purchase_date': vals[8]})

    def _delete_asset(self):
        aid = self._selected_asset_id()
        if aid is None:
            return
        if messagebox.askyesno("Confirm Delete",
                               "Delete this asset?\nAll assignment records will also be removed."):
            self.db.delete_asset(aid)
            self._refresh_assets()

    # ── ASSIGNMENTS TAB ───────────────────────────────────────
    def _build_assignments_tab(self, parent):
        parent.configure(fg_color=C['bg'])
        tb = ctk.CTkFrame(parent, fg_color='transparent')
        tb.pack(fill='x', pady=(8, 10))

        lbl(tb, 'Filter:', font=F['subhead'], color=C['text2']).pack(side='left', padx=(0, 6))
        self.assign_filter = ctk.StringVar(value='All')
        for val in ('All', 'Assigned', 'Returned'):
            ctk.CTkRadioButton(
                tb, text=val, variable=self.assign_filter, value=val,
                command=self._refresh_assignments,
                text_color=C['text'], fg_color=C['accent'],
                border_color=C['border']
            ).pack(side='left', padx=6)

        btn(tb, '📌  Assign Asset',  self._assign_asset,  width=140).pack(side='right', padx=(6, 0))
        btn(tb, '↩  Return Asset',  self._return_asset,
            color=C['success'], hover='#1E8449', width=140).pack(side='right')

        cols   = ['assign_id', 'asset_name', 'asset_type', 'member_name',
                  'assign_date', 'return_date', 'notes', 'status']
        widths = {'assign_id': 60, 'asset_name': 180, 'asset_type': 110,
                  'member_name': 160, 'assign_date': 100, 'return_date': 100,
                  'notes': 180, 'status': 80}
        self.assign_tree = make_treeview(parent, cols, widths, height=18)
        self.assign_tree.container.pack(fill='both', expand=True)
        self._refresh_assignments()

    def _refresh_assignments(self):
        rows = self.db.get_assignments(self.assign_filter.get())
        populate_tree(self.assign_tree, rows,
                      ['assign_id', 'asset_name', 'asset_type', 'member_name',
                       'assign_date', 'return_date', 'notes', 'status'])

    def _selected_assign_id(self):
        sel = self.assign_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an assignment first.")
            return None
        return self.assign_tree.item(sel[0])['values'][0]

    def _assign_asset(self):
        AssignAssetDialog(self, self.db,
                          callback=lambda: (self._refresh_assignments(), self._refresh_assets()))

    def _return_asset(self):
        aid = self._selected_assign_id()
        if aid is None:
            return
        if messagebox.askyesno("Confirm Return", "Mark this asset as returned?"):
            if self.db.return_asset(aid):
                messagebox.showinfo("Success", "Asset returned successfully!")
            self._refresh_assignments()
            self._refresh_assets()


# ══════════════════════════════════════════════════════════════
# ASSET DIALOG  (Add / Edit)
# ══════════════════════════════════════════════════════════════
class AssetDialog(ModalDialog):
    TYPES = ['Laptop', 'Desktop', 'Monitor', 'Peripheral', 'Furniture',
             'Networking', 'Mobile Device', 'Server', 'Other']
    CONDITIONS = ['New', 'Good', 'Fair', 'Poor']

    def __init__(self, parent, db, callback, prefill=None):
        self.db       = db
        self.callback = callback
        self.prefill  = prefill or {}
        title = 'Edit Asset' if prefill else 'Add New Asset'
        super().__init__(parent, title, width=520, height=560)

    def build_form(self):
        p = self.prefill
        self.e_name   = self.form_row('Asset Name *',   entry(self.body, 'e.g. Developer Laptop #3'))
        self.e_brand  = self.form_row('Brand',          entry(self.body, 'e.g. Dell'))
        self.e_model  = self.form_row('Model',          entry(self.body, 'e.g. XPS 15'))
        self.e_serial = self.form_row('Serial Number',  entry(self.body, 'Unique serial number'))
        self.e_pdate  = self.form_row('Purchase Date',  entry(self.body, 'YYYY-MM-DD', width=180))

        # Type dropdown
        tf = ctk.CTkFrame(self.body, fg_color='transparent')
        tf.pack(fill='x', pady=5)
        lbl(tf, 'Asset Type *', font=F['subhead'], color=C['text2']).pack(anchor='w')
        self.type_var = ctk.StringVar(value=p.get('asset_type', 'Laptop'))
        ctk.CTkOptionMenu(tf, values=self.TYPES, variable=self.type_var,
                          width=220, height=36, corner_radius=8,
                          fg_color=C['card'], button_color=C['accent'],
                          text_color=C['text']).pack(anchor='w', pady=(2, 0))

        # Condition dropdown
        cf = ctk.CTkFrame(self.body, fg_color='transparent')
        cf.pack(fill='x', pady=5)
        lbl(cf, 'Condition', font=F['subhead'], color=C['text2']).pack(anchor='w')
        self.cond_var = ctk.StringVar(value=p.get('condition', 'Good'))
        ctk.CTkOptionMenu(cf, values=self.CONDITIONS, variable=self.cond_var,
                          width=160, height=36, corner_radius=8,
                          fg_color=C['card'], button_color=C['accent'],
                          text_color=C['text']).pack(anchor='w', pady=(2, 0))

        if p:
            self.e_name.insert(0,   p.get('asset_name',    ''))
            self.e_brand.insert(0,  p.get('brand',         ''))
            self.e_model.insert(0,  p.get('model',         ''))
            self.e_serial.insert(0, p.get('serial_number', ''))
            
            # Purchase date prefill correction
            pd = p.get('purchase_date', '')
            if pd and pd != '-':
                self.e_pdate.insert(0, pd)

    def on_save(self):
        name   = self.e_name.get().strip()
        brand  = self.e_brand.get().strip()
        model  = self.e_model.get().strip()
        serial = self.e_serial.get().strip() or None
        pdate  = self.e_pdate.get().strip() or None
        atype  = self.type_var.get()
        cond   = self.cond_var.get()

        if not name:
            messagebox.showwarning("Required", "Asset Name is required.", parent=self)
            return
        if pdate:
            try:
                datetime.datetime.strptime(pdate, '%Y-%m-%d')
            except ValueError:
                messagebox.showwarning("Invalid Date",
                                       "Purchase date must be YYYY-MM-DD format.", parent=self)
                return

        if self.prefill:
            self.db.update_asset(self.prefill['id'], name, atype, brand, model,
                                  serial, pdate, cond)
        else:
            self.db.add_asset(name, atype, brand, model, serial, pdate, cond)
        self.callback()
        self.destroy()


# ══════════════════════════════════════════════════════════════
# ASSIGN ASSET DIALOG  (Transaction)
# ══════════════════════════════════════════════════════════════
class AssignAssetDialog(ModalDialog):
    def __init__(self, parent, db, callback):
        self.db       = db
        self.callback = callback
        self._assets  = db.available_asset_dropdown()   # [(id, label), ...]
        self._members = db.member_dropdown()
        super().__init__(parent, 'Assign Asset to Member', width=500, height=360)

    def build_form(self):
        # Renamed variable inside the comprehension to 'albl' to avoid shadowing ui_helpers.lbl
        asset_labels = [albl for _, albl in self._assets]
        
        af = ctk.CTkFrame(self.body, fg_color='transparent')
        af.pack(fill='x', pady=5)
        lbl(af, 'Available Asset *', font=F['subhead'], color=C['text2']).pack(anchor='w')
        self.asset_var = ctk.StringVar(value=asset_labels[0] if asset_labels else 'No available assets')
        ctk.CTkOptionMenu(af, values=asset_labels or ['No available assets'],
                          variable=self.asset_var,
                          width=440, height=36, corner_radius=8,
                          fg_color=C['card'], button_color=C['accent'],
                          text_color=C['text']).pack(anchor='w', pady=(2, 0))

        mf = ctk.CTkFrame(self.body, fg_color='transparent')
        mf.pack(fill='x', pady=5)
        lbl(mf, 'Assign to Member *', font=F['subhead'], color=C['text2']).pack(anchor='w')
        mnames = [n for _, n in self._members]
        self.member_var = ctk.StringVar(value=mnames[0] if mnames else '')
        ctk.CTkOptionMenu(mf, values=mnames or ['No members'],
                          variable=self.member_var,
                          width=440, height=36, corner_radius=8,
                          fg_color=C['card'], button_color=C['accent'],
                          text_color=C['text']).pack(anchor='w', pady=(2, 0))

        nf = ctk.CTkFrame(self.body, fg_color='transparent')
        nf.pack(fill='x', pady=5)
        lbl(nf, 'Notes / Purpose', font=F['subhead'], color=C['text2']).pack(anchor='w')
        self.e_notes = ctk.CTkTextbox(nf, height=70, corner_radius=8,
                                       border_color=C['border'], border_width=1,
                                       fg_color=C['card'], text_color=C['text'])
        self.e_notes.pack(fill='x', pady=(2, 0))

    def on_save(self):
        if not self._assets or not self._members:
            messagebox.showerror("Cannot Assign",
                                 "No available assets or no members exist.", parent=self)
            return
        sel_asset  = self.asset_var.get()
        asset_id   = next((aid for aid, albl in self._assets if albl == sel_asset), None)
        sel_member = self.member_var.get()
        member_id  = next((mid for mid, n in self._members if n == sel_member), None)
        notes      = self.e_notes.get('1.0', 'end').strip()

        if asset_id and member_id:
            if self.db.assign_asset(asset_id, member_id, notes):
                messagebox.showinfo("Success", "Asset assigned successfully!")
            self.callback()
            self.destroy()