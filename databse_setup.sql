-- ==========================================================
-- Database Setup Script for Library & Asset Management System
-- ==========================================================

-- Create the database and use it
CREATE DATABASE IF NOT EXISTS library_asset_db;
USE library_asset_db;

-- Drop tables if they already exist to prevent errors on re-runs (Order matters due to Foreign Keys)
DROP TABLE IF EXISTS Book_Issues;
DROP TABLE IF EXISTS Asset_Assignments;
DROP TABLE IF EXISTS Library_Books;
DROP TABLE IF EXISTS Company_Assets;
DROP TABLE IF EXISTS Members;

-- ══════════════════════════════════════════════════════════
-- 1. MEMBERS TABLE
-- ══════════════════════════════════════════════════════════
CREATE TABLE Members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    department VARCHAR(100) NOT NULL,
    join_date DATE DEFAULT (CURRENT_DATE)
);

-- ══════════════════════════════════════════════════════════
-- 2. LIBRARY BOOKS TABLE
-- ══════════════════════════════════════════════════════════
CREATE TABLE Library_Books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    total_copies INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1,
    added_date DATE DEFAULT (CURRENT_DATE)
);

-- ══════════════════════════════════════════════════════════
-- 3. BOOK ISSUES TABLE
-- ══════════════════════════════════════════════════════════
CREATE TABLE Book_Issues (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    issue_date DATE DEFAULT (CURRENT_DATE),
    due_date DATE NOT NULL,
    return_date DATE DEFAULT NULL,
    status ENUM('Issued', 'Returned') DEFAULT 'Issued',
    FOREIGN KEY (book_id) REFERENCES Library_Books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES Members(member_id) ON DELETE CASCADE
);

-- ══════════════════════════════════════════════════════════
-- 4. COMPANY ASSETS TABLE
-- ══════════════════════════════════════════════════════════
CREATE TABLE Company_Assets (
    asset_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_name VARCHAR(150) NOT NULL,
    asset_type VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    serial_number VARCHAR(100) NOT NULL,
    purchase_date DATE DEFAULT NULL,
    `condition` VARCHAR(50) NOT NULL, 
    status ENUM('Available', 'Assigned', 'Maintenance', 'Retired') DEFAULT 'Available'
);

-- ══════════════════════════════════════════════════════════
-- 5. ASSET ASSIGNMENTS TABLE
-- ══════════════════════════════════════════════════════════
CREATE TABLE Asset_Assignments (
    assign_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    member_id INT NOT NULL,
    assign_date DATE DEFAULT (CURRENT_DATE),
    return_date DATE DEFAULT NULL,
    notes TEXT,
    status ENUM('Assigned', 'Returned') DEFAULT 'Assigned',
    FOREIGN KEY (asset_id) REFERENCES Company_Assets(asset_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES Members(member_id) ON DELETE CASCADE
);

-- ══════════════════════════════════════════════════════════
-- OPTIONAL: INSERT DUMMY DATA FOR TESTING
-- ══════════════════════════════════════════════════════════

INSERT INTO Members (name, email, phone, department, join_date) VALUES 
('Alice Johnson', 'alice.j@company.com', '555-0101', 'Engineering', '2023-01-15'),
('Bob Smith', 'bob.s@company.com', '555-0102', 'Marketing', '2023-03-22'),
('Charlie Brown', 'charlie.b@company.com', '555-0103', 'Human Resources', '2023-06-10');

INSERT INTO Library_Books (title, author, isbn, category, total_copies, available_copies, added_date) VALUES 
('Clean Code', 'Robert C. Martin', '978-0132350884', 'Software Engineering', 5, 4, '2023-01-20'),
('The Pragmatic Programmer', 'Andrew Hunt', '978-0201616224', 'Software Engineering', 3, 3, '2023-02-15'),
('Design of Everyday Things', 'Don Norman', '978-0465050659', 'Design', 2, 2, '2023-04-10');

INSERT INTO Book_Issues (book_id, member_id, issue_date, due_date, status) VALUES 
(1, 1, DATE_SUB(CURDATE(), INTERVAL 10 DAY), DATE_ADD(CURDATE(), INTERVAL 4 DAY), 'Issued');

INSERT INTO Company_Assets (asset_name, asset_type, brand, model, serial_number, purchase_date, `condition`, status) VALUES 
('MacBook Pro M2', 'Laptop', 'Apple', '14-inch 2023', 'C02H89XYZ', '2023-05-01', 'Excellent', 'Assigned'),
('Dell UltraSharp 27', 'Monitor', 'Dell', 'U2720Q', 'CN-0X55XYZ', '2023-05-15', 'Good', 'Available'),
('Logitech MX Master 3', 'Peripherals', 'Logitech', 'MX Master 3', '2138LZXYZ', '2023-05-15', 'Excellent', 'Available');

INSERT INTO Asset_Assignments (asset_id, member_id, assign_date, notes, status) VALUES 
(1, 1, '2023-05-05', 'Standard engineering laptop issue', 'Assigned');