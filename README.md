# Library & Asset Management System 📚💻

A desktop application built with **Python**, **CustomTkinter**, and **MySQL** for managing library books, asset inventories, assignments, and members.

---

## ✨ Features

- **Dashboard**: Real-time KPI statistics for books, members, active issues, total assets, and asset assignments.
- **Library Management**:
  - Catalog management: Add, edit, search, and delete books.
  - Issue & Return tracking with due dates and overdue status detection.
  - Automated stock synchronization on issue and return.
- **Asset Management**:
  - Asset tracking (Laptops, Monitors, Peripherals, etc.) by serial number, category, and status.
  - Assignment workflow: Assign assets to members and track returns.
- **Member Directory**: Manage member records (students/employees), contact details, and department affiliations.
- **Settings & Theme**: Configure database connection parameters and light/dark theme settings.

---

## 🛠️ Tech Stack

- **GUI Framework**: [CustomTkinter](https://customtkinter.tomschimansky.com/) (modern, customizable Tkinter wrapper)
- **Database**: MySQL (compatible with XAMPP / MariaDB / standalone MySQL)
- **Database Driver**: `mysql-connector-python`
- **Language**: Python 3.10+

---

## 📁 Project Architecture

```
library_asset_app/
│
├── main.py               # Application entry point
├── app.py                # Root App window, navigation bar, and routing
├── config.py             # Database configuration, color palette, and font definitions
├── database.py           # DatabaseManager (CRUD queries & transaction handling)
├── ui_helpers.py         # Reusable UI component factories & Treeview styling
├── dialogs.py            # Modal dialog base class
├── databse_setup.sql     # Database schema and seed data
├── requirements.txt      # Python dependencies
│
└── frames/               # Application view modules
    ├── __init__.py       # Frame re-exports
    ├── dashboard.py      # KPI cards & overview
    ├── library.py        # Book catalog, issue/return forms & tables
    ├── assets.py         # Hardware/asset tracking & assignments
    ├── members.py        # Member directory & registration
    └── settings.py       # Configuration & connection settings
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** installed
- **MySQL Server** (e.g., via [XAMPP](https://www.apachefriends.org/))

### 2. Database Setup
1. Start Apache & MySQL in the XAMPP Control Panel.
2. Open **phpMyAdmin** (`http://localhost/phpmyadmin/`).
3. Click the **SQL** tab.
4. Open [databse_setup.sql](databse_setup.sql), copy its contents, paste into the SQL editor, and click **Go**.
   - This creates `library_asset_db` and populates initial sample data.

### 3. Configure Connection
If your MySQL username, password, or port differs from the defaults, update `DB_CONFIG` in `config.py`:

```python
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '',       # Enter your MySQL password here if set
    'database': 'library_asset_db',
    'port':     3306,
}
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Launch Application
```bash
python main.py
```

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
