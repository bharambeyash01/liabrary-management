"""
frames/settings.py
──────────────────
SettingsFrame — shows the active DB_CONFIG values and a
"Test Connection" button that verifies XAMPP is reachable.

Also displays a static About panel with version/stack info.
"""

import customtkinter as ctk
from tkinter import messagebox

from config     import C, F, DB_CONFIG
from ui_helpers import lbl, btn, section_header, divider


# ══════════════════════════════════════════════════════════════
# SETTINGS FRAME
# ══════════════════════════════════════════════════════════════
class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, db, **kw):
        super().__init__(parent, fg_color=C['bg'], **kw)
        self.db = db
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color='transparent')
        hdr.pack(fill='x', padx=24, pady=(20, 8))
        section_header(hdr, '⚙️  Settings', 'Database connection and application info')
        divider(self)

        # Connection details card
        card = ctk.CTkFrame(self, fg_color=C['card'], corner_radius=12)
        card.pack(fill='x', padx=24, pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color='transparent')
        inner.pack(fill='x', padx=24, pady=20)

        lbl(inner, 'Database Connection', font=F['heading'], color=C['text']).pack(anchor='w')
        lbl(inner, 'Edit DB_CONFIG at the top of config.py to change these settings.',
            font=F['small'], color=C['text2']).pack(anchor='w', pady=(2, 12))

        for label, key in [('Host', 'host'), ('User', 'user'),
                           ('Database', 'database'), ('Port', 'port')]:
            row = ctk.CTkFrame(inner, fg_color='transparent')
            row.pack(fill='x', pady=3)
            lbl(row, f'{label}:', font=F['subhead'], color=C['text2'], width=100,
                anchor='w').pack(side='left')
            lbl(row, str(DB_CONFIG.get(key, '')), font=F['body'], color=C['text']
                ).pack(side='left', padx=8)

        btn(inner, '🔌  Test Connection', self._test_connection,
            width=180, color='#6C5CE7', hover='#5A4BD1').pack(anchor='w', pady=(16, 0))

        # About card
        about = ctk.CTkFrame(self, fg_color=C['card'], corner_radius=12)
        about.pack(fill='x', padx=24)
        ai = ctk.CTkFrame(about, fg_color='transparent')
        ai.pack(fill='x', padx=24, pady=20)
        lbl(ai, 'About', font=F['heading'], color=C['text']).pack(anchor='w')
        for line in [
            'Application : Library & Asset Management System',
            'Version     : 1.0.0',
            'Frontend    : Python 3 + customtkinter',
            'Database    : MySQL via XAMPP',
            'Driver      : mysql-connector-python',
        ]:
            lbl(ai, line, font=F['body'], color=C['text2']).pack(anchor='w', pady=1)

    def _test_connection(self):
        if self.db._ensure_connected():
            messagebox.showinfo("Connection OK",
                                "✅  Successfully connected to MySQL!\n\n"
                                f"Host: {DB_CONFIG['host']}\n"
                                f"Database: {DB_CONFIG['database']}")
        else:
            messagebox.showerror("Connection Failed",
                                 "❌  Could not connect.\nCheck XAMPP and DB_CONFIG.")