"""
frames/dashboard.py
───────────────────
DashboardFrame — the home screen shown on startup.

Displays six KPI cards (total books, active issues, overdue,
total assets, assigned assets, total members) pulled live from
the database every time the frame is navigated to.

refresh() is called by App.show_frame() whenever the user
returns to the dashboard so counts are always up-to-date.
"""

import datetime
import customtkinter as ctk

from config     import C, F
from ui_helpers import lbl, btn, section_header, divider


# ══════════════════════════════════════════════════════════════
# DASHBOARD FRAME
# ══════════════════════════════════════════════════════════════
class DashboardFrame(ctk.CTkFrame):
    """Home screen with KPI summary cards."""

    def __init__(self, parent, db, **kw):
        super().__init__(parent, fg_color=C['bg'], **kw)
        self.db = db
        self._build()

    def _build(self):
        # ── Page header
        hdr = ctk.CTkFrame(self, fg_color='transparent')
        hdr.pack(fill='x', padx=24, pady=(24, 8))
        section_header(hdr, '🏠  Dashboard',
                       f'Welcome back  ·  {datetime.date.today().strftime("%A, %d %B %Y")}')
        divider(self)

        # ── Stat cards grid (2 rows × 3 columns)
        grid = ctk.CTkFrame(self, fg_color='transparent')
        grid.pack(fill='x', padx=24, pady=(0, 20))

        # Configure 3 equal columns
        for col in range(3):
            grid.columnconfigure(col, weight=1, uniform='card')

        stats = self.db.get_stats()
        cards = [
            ('📚  Total Books',       stats['total_books'],     C['accent'],   '📖 in the library catalogue'),
            ('📋  Active Issues',     stats['active_issues'],   C['warning'],  '📤 books currently borrowed'),
            ('⚠  Overdue',          stats['overdue'],          C['danger'],   '📅 past their due date'),
            ('💼  Total Assets',      stats['total_assets'],    '#6C5CE7',     '🖥 tracked company assets'),
            ('📌  Assigned Assets',   stats['assigned_assets'], '#00B894',     '👤 currently in use'),
            ('👥  Total Members',     stats['total_members'],   '#FDCB6E',     '🏢 registered employees'),
        ]
        for i, (title, value, color, subtitle) in enumerate(cards):
            r, c = divmod(i, 3)
            self._stat_card(grid, title, value, color, subtitle, row=r, col=c)

        # ── Quick-action section
        divider(self)
        qa_hdr = ctk.CTkFrame(self, fg_color='transparent')
        qa_hdr.pack(fill='x', padx=24, pady=(0, 10))
        lbl(qa_hdr, 'Quick Actions', font=F['heading'], color=C['text']).pack(anchor='w')

        qa = ctk.CTkFrame(self, fg_color='transparent')
        qa.pack(fill='x', padx=24)
        
        # Point the lambdas to the new popup handler method
        actions = [
            ('📤  Issue a Book',    lambda: self._handle_quick_action('issue_book'), C['accent']),
            ('📥  Return a Book',   lambda: self._handle_quick_action('return_book'), C['success']),
            ('📌  Assign Asset',    lambda: self._handle_quick_action('assign_asset'), '#6C5CE7'),
            ('↩  Return Asset',    lambda: self._handle_quick_action('return_asset'), '#00B894'),
        ]
        for text, cmd, color in actions:
            btn(qa, text, cmd, color=color, hover=C['accent_h'], width=160).pack(
                side='left', padx=(0, 10))

        lbl(self, 'Use the sidebar to navigate to a module for full CRUD operations.',
            font=F['small'], color=C['text2']).pack(anchor='w', padx=24, pady=(8, 0))

    def _handle_quick_action(self, action_name: str):
        """Handle quick action popup dialogues."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Quick Action")
        dialog.geometry("400x380")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        # Center the dialog relative to the main window
        dialog.update_idletasks()
        parent = self.winfo_toplevel()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 380) // 2
        dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        # Map logic and fields based on selected action
        configs = {
            'issue_book':   ('📤  Issue a Book',   ['Book ID', 'Member ID'], C['accent']),
            'return_book':  ('📥  Return a Book',  ['Issue ID'], C['success']),
            'assign_asset': ('📌  Assign Asset',   ['Asset ID', 'Member ID'], '#6C5CE7'),
            'return_asset': ('↩  Return Asset',    ['Assign ID'], '#00B894'),
        }
        
        title_text, fields, btn_color = configs[action_name]

        # UI Elements
        lbl(dialog, title_text, font=F['heading'], color=C['text']).pack(pady=(24, 16))
        
        entries = {}
        for field in fields:
            entry = ctk.CTkEntry(dialog, placeholder_text=field, width=280, height=36)
            entry.pack(pady=8)
            entries[field] = entry

        error_lbl = lbl(dialog, "", font=F['small'], color=C['danger'])
        error_lbl.pack(pady=(4, 8))

        def submit():
            data = {f: e.get().strip() for f, e in entries.items()}
            if not all(data.values()):
                error_lbl.configure(text="All fields are required.")
                return
                
            try:
                if action_name == 'issue_book':
                    due_date = datetime.date.today() + datetime.timedelta(days=14)
                    self.db.issue_book(data['Book ID'], data['Member ID'], due_date)
                elif action_name == 'return_book':
                    self.db.return_book(data['Issue ID'])
                elif action_name == 'assign_asset':
                    self.db.assign_asset(data['Asset ID'], data['Member ID'], "Quick assignment from Dashboard")
                elif action_name == 'return_asset':
                    self.db.return_asset(data['Assign ID'])
                    
                # Refresh KPI numbers to immediately show update
                self.refresh()
                dialog.destroy()
            except AttributeError:
                error_lbl.configure(text="Action not implemented in DB module.")
            except Exception as e:
                error_lbl.configure(text=f"Error: {str(e)}")

        btn(dialog, "Submit", submit, color=btn_color, width=280).pack(pady=(16, 8))
        btn(dialog, "Cancel", dialog.destroy, color=C['text2'], hover=C['danger'], width=280).pack()

    def _stat_card(self, parent, title: str, value, accent_color: str,
                   subtitle: str, row: int, col: int):
        """
        Render a single KPI card inside the grid.
        Each card is a white CTkFrame with a coloured top stripe.
        """
        # Outer card frame
        card = ctk.CTkFrame(parent, fg_color=C['card'], corner_radius=12,
                            border_width=0)
        card.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')

        # Coloured top stripe
        stripe = ctk.CTkFrame(card, fg_color=accent_color,
                              corner_radius=0, height=5)
        stripe.pack(fill='x')

        # Card body
        body = ctk.CTkFrame(card, fg_color='transparent')
        body.pack(fill='both', expand=True, padx=18, pady=14)

        lbl(body, title,         font=F['card_lbl'], color=C['text2']).pack(anchor='w')
        lbl(body, str(value),    font=F['card_val'], color=accent_color).pack(anchor='w', pady=(4, 0))
        lbl(body, subtitle,      font=F['small'],    color=C['text2']).pack(anchor='w', pady=(2, 0))

    def refresh(self):
        """Re-render the dashboard to pick up updated counts."""
        for widget in self.winfo_children():
            widget.destroy()
        self._build()