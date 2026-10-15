"""
main.py
───────
Entry point for the Library & Asset Management System.

Run this file to launch the application:
    python main.py

HOW TO SET UP:
  1. Start XAMPP (Apache + MySQL).
  2. Open phpMyAdmin → SQL tab → paste and run database_setup.sql.
  3. Install dependencies:
         pip install customtkinter mysql-connector-python
  4. Run:
         python main.py
"""

from app import App


if __name__ == '__main__':
    app = App()
    # Start the Tkinter event loop — blocks until the window closes
    app.mainloop()