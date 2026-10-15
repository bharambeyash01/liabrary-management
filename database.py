"""
database.py
───────────
DatabaseManager encapsulates every MySQL interaction.
No UI code (no CTk / Tkinter imports) lives here — only the DB driver.

The UI layer imports DatabaseManager and calls its methods;
it never touches mysql.connector directly.
"""

import mysql.connector
from mysql.connector import Error
from tkinter import messagebox          # Used only to surface DB errors to the user

from config import DB_CONFIG            # Credentials from the single config file


# ══════════════════════════════════════════════════════════════
# DATABASE MANAGER
# ══════════════════════════════════════════════════════════════
class DatabaseManager:
    """Handles all MySQL operations with robust error handling."""

    def __init__(self):
        self.connection = None
        self._connect()

    # ── Connection ───────────────────────────────────────────
    def _connect(self):
        """
        Attempt to open a MySQL connection.
        Shows an error dialog and returns False if XAMPP is not running.
        """
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            return self.connection.is_connected()
        except Error as e:
            messagebox.showerror(
                "Connection Failed",
                f"Cannot reach MySQL.\n\nMake sure XAMPP is running "
                f"and the database has been created.\n\nError:\n{e}"
            )
            return False

    def _ensure_connected(self):
        """Auto-reconnect if the connection dropped (e.g., after sleep)."""
        try:
            if self.connection and self.connection.is_connected():
                return True
            return self._connect()
        except Exception:
            return self._connect()

    # ── Universal query executor ──────────────────────────────
    def run(self, query, params=None, *, fetch=False, fetchone=False):
        """
        Execute any SQL query.
        • fetch=True    → SELECT returning all rows  (list of dicts)
        • fetchone=True → SELECT returning first row (dict)
        • default       → INSERT / UPDATE / DELETE   (returns lastrowid)
        """
        try:
            self._ensure_connected()
            # dictionary=True → rows come back as {column: value} dicts
            cur = self.connection.cursor(dictionary=True)
            cur.execute(query, params or ())
            if fetch:
                result = cur.fetchall()
                cur.close()
                return result
            if fetchone:
                result = cur.fetchone()
                cur.close()
                return result
            # DML statement — commit and return the new row's id
            self.connection.commit()
            last_id = cur.lastrowid
            cur.close()
            return last_id
        except Error as e:
            messagebox.showerror("Database Error", f"Query failed:\n\n{e}")
            try:
                self.connection.rollback()
            except Exception:
                pass
            return None

    # ── DASHBOARD ────────────────────────────────────────────
    def get_stats(self):
        """Return a dict of summary counts for the Dashboard cards."""
        def count(q, p=None):
            r = self.run(q, p, fetchone=True)
            return (r or {}).get('c', 0)

        return {
            'total_books':      count("SELECT COUNT(*) c FROM Library_Books"),
            'active_issues':    count("SELECT COUNT(*) c FROM Book_Issues WHERE status='Issued'"),
            'overdue':          count("SELECT COUNT(*) c FROM Book_Issues WHERE status='Issued' AND due_date < CURDATE()"),
            'total_assets':     count("SELECT COUNT(*) c FROM Company_Assets"),
            'assigned_assets':  count("SELECT COUNT(*) c FROM Asset_Assignments WHERE status='Assigned'"),
            'total_members':    count("SELECT COUNT(*) c FROM Members"),
        }

    # ── MEMBERS ──────────────────────────────────────────────
    def get_members(self, search=''):
        q = """SELECT member_id,
                      name, email, phone, department,
                      DATE_FORMAT(join_date,'%d %b %Y') AS join_date
               FROM Members
               WHERE name LIKE %s OR email LIKE %s OR department LIKE %s
               ORDER BY name"""
        s = f'%{search}%'
        return self.run(q, (s, s, s), fetch=True) or []

    def add_member(self, name, email, phone, dept):
        return self.run(
            "INSERT INTO Members (name,email,phone,department) VALUES (%s,%s,%s,%s)",
            (name, email, phone, dept))

    def update_member(self, mid, name, email, phone, dept):
        return self.run(
            "UPDATE Members SET name=%s,email=%s,phone=%s,department=%s WHERE member_id=%s",
            (name, email, phone, dept, mid))

    def delete_member(self, mid):
        return self.run("DELETE FROM Members WHERE member_id=%s", (mid,))

    def member_dropdown(self):
        """Returns list of (id, name) for dropdown menus."""
        rows = self.run("SELECT member_id, name FROM Members ORDER BY name", fetch=True) or []
        return [(r['member_id'], r['name']) for r in rows]

    # ── BOOKS ────────────────────────────────────────────────
    def get_books(self, search=''):
        q = """SELECT book_id, title, author, isbn, category,
                      total_copies, available_copies,
                      DATE_FORMAT(added_date,'%d %b %Y') AS added_date
               FROM Library_Books
               WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s
               ORDER BY title"""
        s = f'%{search}%'
        return self.run(q, (s, s, s), fetch=True) or []

    def add_book(self, title, author, isbn, category, copies):
        return self.run(
            """INSERT INTO Library_Books
               (title,author,isbn,category,total_copies,available_copies)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (title, author, isbn, category, copies, copies))

    def update_book(self, bid, title, author, isbn, category, copies):
        return self.run(
            """UPDATE Library_Books
               SET title=%s,author=%s,isbn=%s,category=%s,total_copies=%s
               WHERE book_id=%s""",
            (title, author, isbn, category, copies, bid))

    def delete_book(self, bid):
        return self.run("DELETE FROM Library_Books WHERE book_id=%s", (bid,))

    def book_dropdown(self):
        rows = self.run(
            "SELECT book_id, title, available_copies FROM Library_Books ORDER BY title",
            fetch=True) or []
        return [(r['book_id'], r['title'], r['available_copies']) for r in rows]

    # ── BOOK ISSUES ──────────────────────────────────────────
    def get_issues(self, status='All'):
        q = """SELECT bi.issue_id,
                      b.title        AS book_title,
                      m.name         AS member_name,
                      DATE_FORMAT(bi.issue_date,'%d %b %Y')  AS issue_date,
                      DATE_FORMAT(bi.due_date,  '%d %b %Y')  AS due_date,
                      IFNULL(DATE_FORMAT(bi.return_date,'%d %b %Y'),'-') AS return_date,
                      bi.status,
                      IF(bi.due_date < CURDATE() AND bi.status='Issued','YES','NO') AS overdue
               FROM Book_Issues bi
               JOIN Library_Books b ON bi.book_id   = b.book_id
               JOIN Members       m ON bi.member_id = m.member_id
               {where}
               ORDER BY bi.issue_date DESC"""
        where = '' if status == 'All' else 'WHERE bi.status=%s'
        params = () if status == 'All' else (status,)
        return self.run(q.format(where=where), params, fetch=True) or []

    def issue_book(self, book_id, member_id, due_date):
        book = self.run(
            "SELECT available_copies FROM Library_Books WHERE book_id=%s",
            (book_id,), fetchone=True)
        if not book or book['available_copies'] < 1:
            messagebox.showerror("Not Available", "No copies of this book are available!")
            return None
        self.run("INSERT INTO Book_Issues (book_id,member_id,due_date) VALUES (%s,%s,%s)",
                 (book_id, member_id, due_date))
        self.run("UPDATE Library_Books SET available_copies=available_copies-1 WHERE book_id=%s",
                 (book_id,))
        return True

    def return_book(self, issue_id):
        issue = self.run(
            "SELECT book_id, status FROM Book_Issues WHERE issue_id=%s",
            (issue_id,), fetchone=True)
        if not issue or issue['status'] == 'Returned':
            messagebox.showwarning("Already Returned", "This book was already returned.")
            return None
        self.run("UPDATE Book_Issues SET status='Returned',return_date=CURDATE() WHERE issue_id=%s",
                 (issue_id,))
        self.run("UPDATE Library_Books SET available_copies=available_copies+1 WHERE book_id=%s",
                 (issue['book_id'],))
        return True

    # ── ASSETS ───────────────────────────────────────────────
    def get_assets(self, search=''):
        q = """SELECT asset_id, asset_name, asset_type, brand, model,
                      serial_number, `condition`, status,
                      IFNULL(DATE_FORMAT(purchase_date,'%d %b %Y'),'-') AS purchase_date
               FROM Company_Assets
               WHERE asset_name LIKE %s OR asset_type LIKE %s OR serial_number LIKE %s
               ORDER BY asset_name"""
        s = f'%{search}%'
        return self.run(q, (s, s, s), fetch=True) or []

    def add_asset(self, name, atype, brand, model, serial, pdate, condition):
        return self.run(
            """INSERT INTO Company_Assets
               (asset_name,asset_type,brand,model,serial_number,purchase_date,`condition`)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (name, atype, brand, model, serial, pdate or None, condition))

    def update_asset(self, aid, name, atype, brand, model, serial, pdate, condition):
        return self.run(
            """UPDATE Company_Assets
               SET asset_name=%s,asset_type=%s,brand=%s,model=%s,
                   serial_number=%s,purchase_date=%s,`condition`=%s
               WHERE asset_id=%s""",
            (name, atype, brand, model, serial, pdate or None, condition, aid))

    def delete_asset(self, aid):
        return self.run("DELETE FROM Company_Assets WHERE asset_id=%s", (aid,))

    def available_asset_dropdown(self):
        rows = self.run(
            "SELECT asset_id,asset_name,asset_type FROM Company_Assets WHERE status='Available' ORDER BY asset_name",
            fetch=True) or []
        return [(r['asset_id'], f"{r['asset_name']} ({r['asset_type']})") for r in rows]

    # ── ASSET ASSIGNMENTS ─────────────────────────────────────
    def get_assignments(self, status='All'):
        q = """SELECT aa.assign_id,
                      a.asset_name, a.asset_type,
                      m.name        AS member_name,
                      DATE_FORMAT(aa.assign_date,'%d %b %Y') AS assign_date,
                      IFNULL(DATE_FORMAT(aa.return_date,'%d %b %Y'),'-') AS return_date,
                      IFNULL(aa.notes,'-') AS notes,
                      aa.status
               FROM Asset_Assignments aa
               JOIN Company_Assets a ON aa.asset_id  = a.asset_id
               JOIN Members        m ON aa.member_id = m.member_id
               {where}
               ORDER BY aa.assign_date DESC"""
        where = '' if status == 'All' else 'WHERE aa.status=%s'
        params = () if status == 'All' else (status,)
        return self.run(q.format(where=where), params, fetch=True) or []

    def assign_asset(self, asset_id, member_id, notes):
        asset = self.run(
            "SELECT status FROM Company_Assets WHERE asset_id=%s",
            (asset_id,), fetchone=True)
        if not asset or asset['status'] != 'Available':
            messagebox.showerror("Not Available", "This asset is not available for assignment!")
            return None
        self.run("INSERT INTO Asset_Assignments (asset_id,member_id,notes) VALUES (%s,%s,%s)",
                 (asset_id, member_id, notes))
        self.run("UPDATE Company_Assets SET status='Assigned' WHERE asset_id=%s", (asset_id,))
        return True

    def return_asset(self, assign_id):
        assign = self.run(
            "SELECT asset_id, status FROM Asset_Assignments WHERE assign_id=%s",
            (assign_id,), fetchone=True)
        if not assign or assign['status'] == 'Returned':
            messagebox.showwarning("Already Returned", "This asset was already returned.")
            return None
        self.run("UPDATE Asset_Assignments SET status='Returned',return_date=CURDATE() WHERE assign_id=%s",
                 (assign_id,))
        self.run("UPDATE Company_Assets SET status='Available' WHERE asset_id=%s",
                 (assign['asset_id'],))
        return True

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()