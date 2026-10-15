"""
config.py
─────────
Single source of truth for:
  • DB_CONFIG  — MySQL connection parameters
  • C          — colour palette (all hex strings)
  • F          — font tuples
  • CTK theme  — set once here; every other module just imports C and F

Edit DB_CONFIG to match your XAMPP setup.
Edit C / F to retheme the whole application from one file.
"""

import customtkinter as ctk

# ══════════════════════════════════════════════════════════════
# DATABASE CREDENTIALS
# ── Edit these to match your XAMPP / MySQL installation ──────
# ══════════════════════════════════════════════════════════════
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '',           # Default XAMPP MySQL has no password
    'database': 'library_asset_db',
    'port':     3306,
}

# ══════════════════════════════════════════════════════════════
# CUSTOMTKINTER GLOBAL THEME
# These two calls must happen before any CTk widget is created.
# Importing this module is enough to trigger them.
# ══════════════════════════════════════════════════════════════
ctk.set_appearance_mode("light")    # Force light mode
ctk.set_default_color_theme("blue") # Base colour theme

# ══════════════════════════════════════════════════════════════
# COLOUR PALETTE
# All UI colours live here. Widgets reference C['key'] so a
# colour change means editing one value in one place.
# ══════════════════════════════════════════════════════════════
C = {
    # ── Backgrounds ─────────────────────────────────────────
    'bg':           '#F0F4F8',   # App-wide background (cool light gray)
    'card':         '#FFFFFF',   # Card / panel backgrounds
    'sidebar':      '#1B2A4A',   # Sidebar dark navy
    'sidebar_h':    '#2C3E6B',   # Sidebar hover
    'sidebar_act':  '#2E86AB',   # Active nav item fill
    'header':       '#FFFFFF',   # Top header bar

    # ── Accent / action colours ───────────────────────────
    'accent':       '#2E86AB',   # Primary blue-teal
    'accent_h':     '#1A6E90',   # Accent on hover
    'success':      '#27AE60',   # Green  — "Return" buttons
    'warning':      '#E67E22',   # Orange — warnings / overdue badges
    'danger':       '#E74C3C',   # Red    — delete actions

    # ── Text ─────────────────────────────────────────────
    'text':         '#1A202C',   # Primary body text
    'text2':        '#718096',   # Muted / label text
    'txt_sidebar':  '#B8C5D6',   # Sidebar inactive label
    'white':        '#FFFFFF',

    # ── Borders & Treeview ────────────────────────────────
    'border':       '#DDE3ED',
    'tree_head_bg': '#EDF2F7',   # Treeview header fill
    'tree_alt':     '#F7FAFC',   # Alternate row colour
    'tree_sel':     '#BEE3F8',   # Selected row highlight
}

# ══════════════════════════════════════════════════════════════
# FONT MAP
# Tuples of (family, size) or (family, size, weight).
# Widgets reference F['key'] for consistent typography.
# ══════════════════════════════════════════════════════════════
F = {
    'app_title': ('Segoe UI', 14, 'bold'),
    'title':     ('Segoe UI', 20, 'bold'),
    'heading':   ('Segoe UI', 13, 'bold'),
    'subhead':   ('Segoe UI', 11, 'bold'),
    'body':      ('Segoe UI', 11),
    'small':     ('Segoe UI', 10),
    'sidebar':   ('Segoe UI', 12),
    'sidebar_sm':('Segoe UI', 10),
    'card_val':  ('Segoe UI', 30, 'bold'),
    'card_lbl':  ('Segoe UI', 11),
    'btn':       ('Segoe UI', 11, 'bold'),
    'badge':     ('Segoe UI', 9,  'bold'),
}