"""
app.py
──────
App — the root CTk window.

Responsibilities:
  • Creates the fixed sidebar with nav buttons.
  • Creates the right-side content area.
  • Lazily instantiates and shows frame classes on demand.
  • Passes the shared DatabaseManager instance to every frame.
  • Closes the DB connection cleanly on window close.

Layout:
  ┌──────────┬─────────────────────────────────────┐
  │  SIDEBAR │  CONTENT  (one frame visible at a   │
  │  220 px  │  time; others hidden with pack_     │
  │  (fixed) │  forget)                            │
  └──────────┴─────────────────────────────────────┘
"""

import customtkinter as ctk

from config    import C, F
from database  import DatabaseManager
from ui_helpers import lbl
from frames    import DashboardFrame, LibraryFrame, AssetFrame, MembersFrame, SettingsFrame


# ══════════════════════════════════════════════════════════════
# MAIN APPLICATION WINDOW
# ══════════════════════════════════════════════════════════════
class App(ctk.CTk):
    """
    Root window.
    Layout:
      ┌──────────┬─────────────────────────────┐
      │  SIDEBAR │  CONTENT (swapped by nav)   │
      │  200 px  │  fill remaining width       │
      └──────────┴─────────────────────────────┘
    """

    SIDEBAR_W = 220   # Fixed sidebar width in pixels

    def __init__(self):
        super().__init__()

        # ── Window setup
        self.title('Library & Asset Management System')
        self.geometry('1200x760')
        self.minsize(900, 600)
        self.configure(fg_color=C['bg'])

        # ── Database
        self.db = DatabaseManager()

        # ── Build UI
        self._build_sidebar()
        self._build_content_area()

        # ── Show Dashboard by default
        self._frames: dict[str, ctk.CTkFrame] = {}
        self._active_btn = None
        self.show_frame('dashboard')

        # ── Window close handler
        self.protocol('WM_DELETE_WINDOW', self._on_close)

    # ── SIDEBAR ───────────────────────────────────────────────
    def _build_sidebar(self):
        """
        The sidebar is a fixed-width CTkFrame on the left.
        It contains:
          • App logo / title at the top
          • Navigation buttons (one per module)
          • Version info at the bottom
        """
        self.sidebar = ctk.CTkFrame(
            self,
            width=self.SIDEBAR_W,
            fg_color=C['sidebar'],
            corner_radius=0
        )
        # pack with fill='y' so it always covers the full height
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)   # Prevent children from resizing this frame

        # ── App logo / brand
        brand = ctk.CTkFrame(self.sidebar, fg_color='transparent', height=72)
        brand.pack(fill='x', pady=(8, 0))
        brand.pack_propagate(False)
        lbl(brand, '📦', font=('Segoe UI', 28), color=C['sidebar_act']).pack(pady=(10, 0))
        lbl(brand, 'LibAsset', font=F['app_title'], color=C['white']).pack()

        # Thin separator under logo
        ctk.CTkFrame(self.sidebar, fg_color='#2C3E6B', height=1).pack(
            fill='x', padx=14, pady=10)

        # ── Navigation items
        self._nav_btns: dict[str, ctk.CTkButton] = {}
        nav_items = [
            ('dashboard', '🏠', 'Dashboard'),
            ('library',   '📚', 'Library'),
            ('assets',    '💼', 'Assets'),
            ('members',   '👥', 'Members'),
            ('settings',  '⚙️', 'Settings'),
        ]
        for key, icon, label in nav_items:
            b = self._nav_button(key, icon, label)
            self._nav_btns[key] = b

        # ── Sidebar footer
        ctk.CTkFrame(self.sidebar, fg_color='#2C3E6B', height=1).pack(
            fill='x', padx=14, pady=10, side='bottom')
        lbl(self.sidebar, 'v1.0.0  ·  MySQL', font=F['sidebar_sm'],
            color='#4A5A7A').pack(side='bottom', pady=(0, 10))

    def _nav_button(self, key: str, icon: str, label: str) -> ctk.CTkButton:
        """
        Create a single nav button.
        • Inactive: transparent background, muted text
        • Active:   accent-colour background, white text
        Clicking calls show_frame(key).
        """
        b = ctk.CTkButton(
            self.sidebar,
            text=f'  {icon}  {label}',
            command=lambda k=key: self.show_frame(k),
            anchor='w',
            height=44,
            width=self.SIDEBAR_W - 16,
            corner_radius=8,
            font=F['sidebar'],
            fg_color='transparent',
            hover_color=C['sidebar_h'],
            text_color=C['txt_sidebar'],
        )
        b.pack(padx=8, pady=2)
        return b

    def _set_active_nav(self, key: str):
        """Update nav button colours to reflect the active page."""
        for k, b in self._nav_btns.items():
            if k == key:
                b.configure(fg_color=C['sidebar_act'], text_color=C['white'])
            else:
                b.configure(fg_color='transparent', text_color=C['txt_sidebar'])

    # ── CONTENT AREA ──────────────────────────────────────────
    def _build_content_area(self):
        """
        Right-side content area expands to fill remaining space.
        Frames are created lazily and placed on top of each other;
        show_frame() raises the right one.
        """
        self.content = ctk.CTkFrame(self, fg_color=C['bg'], corner_radius=0)
        self.content.pack(side='left', fill='both', expand=True)

    def show_frame(self, key: str):
        """
        Lazy-instantiate (first visit) and display the requested frame.
        Any previously visible frame is hidden with pack_forget().
        """
        # Hide whatever is currently shown
        for f in self._frames.values():
            f.pack_forget()

        # Create frame on first visit
        if key not in self._frames:
            frame_classes = {
                'dashboard': DashboardFrame,
                'library':   LibraryFrame,
                'assets':    AssetFrame,
                'members':   MembersFrame,
                'settings':  SettingsFrame,
            }
            cls = frame_classes[key]
            self._frames[key] = cls(self.content, self.db)

        # If navigating back to Dashboard, refresh the stats
        if key == 'dashboard':
            dash = self._frames['dashboard']
            dash.refresh()

        # Show the target frame
        self._frames[key].pack(fill='both', expand=True)
        self._set_active_nav(key)

    # ── CLEANUP ───────────────────────────────────────────────
    def _on_close(self):
        """Close DB connection gracefully before destroying the window."""
        self.db.close()
        self.destroy()