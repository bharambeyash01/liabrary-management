"""
frames/library.py
─────────────────
LibraryFrame      — two-tab view: Books catalogue + Issues & Returns.
BookDialog        — Add / Edit popup for a single book record.
IssueBookDialog   — Transaction popup to issue a book to a member.

All three are co-located because the dialogs are only ever
opened from within LibraryFrame.
"""

import datetime
import customtkinter as ctk
from tkinter import messagebox

from config     import C, F
from ui_helpers import lbl, btn, entry, make_treeview, populate_tree, section_header, divider
from dialogs    import ModalDialog


# ══════════════════════════════════════════════════════════════
# LIBRARY FRAME
# ══════════════════════════════════════════════════════════════
class LibraryFrame(ctk.CTkFrame):
    """Library Management — Books catalogue + Issue / Return tracking."""

    def __init__(self, parent, db, **kw):
        super().__init__(parent, fg_color=C['bg'], **kw)
        self.db = db
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color='transparent')
        hdr.pack(fill='x', padx=24, pady=(20, 8))
        section_header(hdr, '📚  Library Management',
                       'Manage books, track issues and returns')
        divider(self)

        # ── Tab view for Books vs Issues
        # CTkTabview gives us a modern pill-style tab switcher
        tabs = ctk.CTkTabview(self, fg_color=C['bg'],
                      segmented_button_fg_color=C['border'],
                      segmented_button_selected_color=C['accent'],
                      segmented_button_selected_hover_color=C['accent_h'],
                      segmented_button_unselected_color='#2E4057',        # ← dark, visible
                      segmented_button_unselected_hover_color='#3A5068',  # ← slightly lighter on hover
                      text_color=C['white'],
                      text_color_disabled='#A0AEC0')
        tabs.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        tabs.add('📖  Books')
        tabs.add('📋  Issues & Returns')

        self._build_books_tab(tabs.tab('📖  Books'))
        self._build_issues_tab(tabs.tab('📋  Issues & Returns'))

    # ── BOOKS TAB ─────────────────────────────────────────────
    def _build_books_tab(self, parent):
        parent.configure(fg_color=C['bg'])

        # Toolbar
        tb = ctk.CTkFrame(parent, fg_color='transparent')
        tb.pack(fill='x', pady=(8, 10))

        self.book_search = ctk.StringVar()
        self.book_search.trace_add('write', lambda *_: self._refresh_books())
        ctk.CTkEntry(tb, textvariable=self.book_search,
                     placeholder_text='🔍  Search title, author or ISBN …',
                     width=300, height=36, corner_radius=8,
                     border_color=C['border'], fg_color=C['card'],
                     text_color=C['text'],
                     placeholder_text_color=C['text2']).pack(side='left')

        btn(tb, '＋  Add Book',  self._add_book,    width=120).pack(side='right', padx=(6, 0))
        btn(tb, '✎  Edit',      self._edit_book,
            color='#6C757D', hover='#5A6268', width=90).pack(side='right', padx=4)
        btn(tb, '🗑  Delete',   self._delete_book,
            color=C['danger'], hover='#C0392B', width=90).pack(side='right')

        # Treeview
        cols   = ['book_id', 'title', 'author', 'isbn', 'category',
                  'total_copies', 'available_copies', 'added_date']
        widths = {'book_id': 55, 'title': 220, 'author': 160, 'isbn': 130,
                  'category': 110, 'total_copies': 80, 'available_copies': 90,
                  'added_date': 110}
        self.book_tree = make_treeview(parent, cols, widths, height=18)
        self.book_tree.container.pack(fill='both', expand=True)
        self._refresh_books()

    def _refresh_books(self):
        rows = self.db.get_books(self.book_search.get())
        populate_tree(self.book_tree, rows,
                      ['book_id', 'title', 'author', 'isbn', 'category',
                       'total_copies', 'available_copies', 'added_date'])

    def _selected_book_id(self):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a book first.")
            return None
        return self.book_tree.item(sel[0])['values'][0]

    def _add_book(self):
        BookDialog(self, self.db, callback=self._refresh_books)

    def _edit_book(self):
        bid = self._selected_book_id()
        if bid is None:
            return
        vals = self.book_tree.item(self.book_tree.selection()[0])['values']
        BookDialog(self, self.db, callback=self._refresh_books,
                   prefill={'id': bid, 'title': vals[1], 'author': vals[2],
                            'isbn': vals[3], 'category': vals[4],
                            'total_copies': vals[5]})

    def _delete_book(self):
        bid = self._selected_book_id()
        if bid is None:
            return
        if messagebox.askyesno("Confirm Delete",
                               "Delete this book?\nAll issue records for it will also be removed."):
            self.db.delete_book(bid)
            self._refresh_books()

    # ── ISSUES TAB ────────────────────────────────────────────
    def _build_issues_tab(self, parent):
        parent.configure(fg_color=C['bg'])

        # Filter + action toolbar
        tb = ctk.CTkFrame(parent, fg_color='white', border_color=C['border'], border_width=1, corner_radius=8)
        tb.pack(fill='x', pady=(8, 10))

        lbl(tb, 'Filter:', font=F['subhead'], color=C['text2']).pack(side='left', padx=(0, 6))
        self.issue_filter = ctk.StringVar(value='All')
        for val in ('All', 'Issued', 'Returned'):
            ctk.CTkRadioButton(
                tb, text=val, variable=self.issue_filter, value=val,
                command=self._refresh_issues,
                text_color=C['text'],
                fg_color=C['accent'],
                border_color=C['border']
            ).pack(side='left', padx=6)

        btn(tb, '📤  Issue Book',  self._issue_book,  width=130).pack(side='right', padx=(6, 0))
        btn(tb, '📥  Return Book', self._return_book,
            color=C['success'], hover='#1E8449', width=130).pack(side='right')

        # Legend
        lbl(tb, '⚠ Yellow row = Overdue', font=F['small'], color=C['warning']).pack(
            side='left', padx=18)

        # Treeview
        cols   = ['issue_id', 'book_title', 'member_name', 'issue_date',
                  'due_date', 'return_date', 'status']
        widths = {'issue_id': 60, 'book_title': 220, 'member_name': 160,
                  'issue_date': 100, 'due_date': 100, 'return_date': 110, 'status': 80}
        self.issue_tree = make_treeview(parent, cols, widths, height=18)
        self.issue_tree.container.pack(fill='both', expand=True)
        self._refresh_issues()

    def _refresh_issues(self):
        rows = self.db.get_issues(self.issue_filter.get())
        populate_tree(self.issue_tree, rows,
                      ['issue_id', 'book_title', 'member_name', 'issue_date',
                       'due_date', 'return_date', 'status'])

    def _selected_issue_id(self):
        sel = self.issue_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an issue record first.")
            return None
        return self.issue_tree.item(sel[0])['values'][0]

    def _issue_book(self):
        IssueBookDialog(self, self.db, callback=self._refresh_issues)

    def _return_book(self):
        iid = self._selected_issue_id()
        if iid is None:
            return
        if messagebox.askyesno("Confirm Return", "Mark this book as returned?"):
            if self.db.return_book(iid):
                messagebox.showinfo("Success", "Book returned successfully!")
            self._refresh_issues()


# ══════════════════════════════════════════════════════════════
# BOOK DIALOG  (Add / Edit)
# ══════════════════════════════════════════════════════════════
class BookDialog(ModalDialog):
    CATEGORIES = ['Technology', 'Science', 'Business', 'Self-Help',
                  'Non-Fiction', 'Fiction', 'History', 'Other']

    def __init__(self, parent, db, callback, prefill=None):
        self.db       = db
        self.callback = callback
        self.prefill  = prefill or {}
        title = 'Edit Book' if prefill else 'Add New Book'
        super().__init__(parent, title, width=500, height=500)

    def build_form(self):
        p = self.prefill
        self.e_title  = self.form_row('Title *',       entry(self.body, 'Book title'))
        self.e_author = self.form_row('Author *',      entry(self.body, 'Author name'))
        self.e_isbn   = self.form_row('ISBN',          entry(self.body, 'e.g. 9780132350884'))
        self.e_copies = self.form_row('Total Copies *',entry(self.body, '1', width=120))

        # Category dropdown
        cat_frame = ctk.CTkFrame(self.body, fg_color='transparent')
        cat_frame.pack(fill='x', pady=5)
        lbl(cat_frame, 'Category', font=F['subhead'], color=C['text2']).pack(anchor='w')
        self.cat_var = ctk.StringVar(value=p.get('category', 'Technology'))
        ctk.CTkOptionMenu(cat_frame, values=self.CATEGORIES, variable=self.cat_var,
                          width=220, height=36, corner_radius=8,
                          fg_color=C['card'], button_color=C['accent'],
                          text_color=C['text']).pack(anchor='w', pady=(2, 0))

        if p:
            self.e_title.insert(0,  p.get('title',       ''))
            self.e_author.insert(0, p.get('author',      ''))
            self.e_isbn.insert(0,   p.get('isbn',        ''))
            self.e_copies.insert(0, p.get('total_copies','1'))

    def on_save(self):
        title  = self.e_title.get().strip()
        author = self.e_author.get().strip()
        isbn   = self.e_isbn.get().strip() or None
        cat    = self.cat_var.get()
        try:
            copies = int(self.e_copies.get().strip())
            assert copies >= 1
        except Exception:
            messagebox.showwarning("Invalid", "Total copies must be a positive integer.", parent=self)
            return
        if not title or not author:
            messagebox.showwarning("Required", "Title and Author are required.", parent=self)
            return
        if self.prefill:
            self.db.update_book(self.prefill['id'], title, author, isbn, cat, copies)
        else:
            self.db.add_book(title, author, isbn, cat, copies)
        self.callback()
        self.destroy()


# ══════════════════════════════════════════════════════════════
# ISSUE BOOK DIALOG  (Transaction)
# ══════════════════════════════════════════════════════════════
class IssueBookDialog(ModalDialog):
    def __init__(self, parent, db, callback):
        self.db       = db
        self.callback = callback
        self._books   = db.book_dropdown()       # [(id, title, avail), ...]
        self._members = db.member_dropdown()     # [(id, name), ...]
        super().__init__(parent, 'Issue a Book', width=500, height=380)

    def build_form(self):
        # Book picker (only shows available books)
        avail = [f"{t} (avail: {a})" for _, t, a in self._books if a > 0]
        self._avail_books = [(bid, t, a) for bid, t, a in self._books if a > 0]

        bf = ctk.CTkFrame(self.body, fg_color='transparent')
        bf.pack(fill='x', pady=5)
        lbl(bf, 'Book *', font=F['subhead'], color=C['text2']).pack(anchor='w')
        self.book_var = ctk.StringVar(value=avail[0] if avail else 'No books available')
        ctk.CTkOptionMenu(bf, values=avail or ['No available books'],
                          variable=self.book_var,
                          width=440, height=36, corner_radius=8,
                          fg_color=C['card'], button_color=C['accent'],
                          text_color=C['text']).pack(anchor='w', pady=(2, 0))

        # Member picker
        mf = ctk.CTkFrame(self.body, fg_color='transparent')
        mf.pack(fill='x', pady=5)
        lbl(mf, 'Member *', font=F['subhead'], color=C['text2']).pack(anchor='w')
        mnames = [n for _, n in self._members]
        self.member_var = ctk.StringVar(value=mnames[0] if mnames else '')
        ctk.CTkOptionMenu(mf, values=mnames or ['No members'],
                          variable=self.member_var,
                          width=440, height=36, corner_radius=8,
                          fg_color=C['card'], button_color=C['accent'],
                          text_color=C['text']).pack(anchor='w', pady=(2, 0))

        # Due date
        df = ctk.CTkFrame(self.body, fg_color='transparent')
        df.pack(fill='x', pady=5)
        lbl(df, 'Due Date *  (YYYY-MM-DD)', font=F['subhead'], color=C['text2']).pack(anchor='w')
        default_due = (datetime.date.today() + datetime.timedelta(days=14)).strftime('%Y-%m-%d')
        self.e_due = entry(df, default_due, width=220)
        self.e_due.insert(0, default_due)
        self.e_due.pack(anchor='w', pady=(2, 0))

    def on_save(self):
        if not self._avail_books or not self._members:
            messagebox.showerror("Cannot Issue",
                                 "No available books or no members exist.", parent=self)
            return
        # Match selected book label back to its ID
        sel_label  = self.book_var.get()
        book_id    = next((bid for bid, t, a in self._avail_books
                           if sel_label.startswith(t)), None)
        sel_member = self.member_var.get()
        member_id  = next((mid for mid, n in self._members if n == sel_member), None)
        due_str    = self.e_due.get().strip()

        try:
            due = datetime.datetime.strptime(due_str, '%Y-%m-%d').date()
            assert due >= datetime.date.today()
        except Exception:
            messagebox.showwarning("Invalid Date",
                                   "Due date must be today or later (YYYY-MM-DD).", parent=self)
            return

        if book_id and member_id:
            if self.db.issue_book(book_id, member_id, due):
                messagebox.showinfo("Success", "Book issued successfully!")
            self.callback()
            self.destroy()