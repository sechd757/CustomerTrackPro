-- Database schema for Customer Logging System

-- Create database
CREATE DATABASE IF NOT EXISTS customer_log CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE customer_log;

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Create initial admin user (password: admin123)
INSERT INTO users (username, password, full_name, is_admin, is_active)
VALUES ('admin', '$2a$10$8KsRftV2waCUkTzT7CXep.h5.7/bHQxnXc7qlZIUVVXgbHKlfkEP.', 'Administrator', TRUE, TRUE);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user VARCHAR(50) NOT NULL,
    name TEXT NOT NULL, -- Encrypted
    name_token VARCHAR(255) NOT NULL, -- Searchable token for name
    phone TEXT NOT NULL, -- Encrypted
    phone_token VARCHAR(255) NOT NULL, -- Searchable token for phone
    email VARCHAR(100),
    city VARCHAR(100),
    stackno VARCHAR(50),
    sales1 VARCHAR(100),
    sales2 VARCHAR(100),
    closer VARCHAR(100),
    newused ENUM('New', 'Used') DEFAULT 'New',
    year VARCHAR(4),
    make VARCHAR(50),
    model VARCHAR(50),
    trade VARCHAR(255),
    demo ENUM('Yes', 'No') DEFAULT 'No',
    writeup TEXT,
    results TEXT,
    notes TEXT,
    datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (name_token),
    INDEX (phone_token),
    INDEX (email),
    INDEX (city),
    INDEX (sales1),
    INDEX (datetime)
) ENGINE=InnoDB;
