#!/usr/bin/env python3
"""
Simple Python server to demonstrate the Customer Logging System
This serves as a demo of the Perl application structure
"""

import http.server
import socketserver
import os
import json
import bcrypt
from urllib.parse import parse_qs, urlparse

# Sample data to mock the customer database
CUSTOMERS = [
    {
        "id": 1,
        "name": "John Doe",
        "phone": "(555) 123-4567",
        "email": "john@example.com",
        "city": "New York",
        "stackno": "A123",
        "sales1": "Jane Smith",
        "sales2": "Bob Johnson",
        "closer": "Alice Brown",
        "newused": "New",
        "year": "2023",
        "make": "Toyota",
        "model": "Camry",
        "trade": "Yes",
        "demo": "No",
        "writeup": "Customer is interested in financing options",
        "results": "Pending final approval",
        "notes": "Follow up next week",
        "datetime": "2023-05-15 14:30:00"
    },
    {
        "id": 2,
        "name": "Jane Smith",
        "phone": "(555) 987-6543",
        "email": "jane@example.com",
        "city": "Chicago",
        "stackno": "B456",
        "sales1": "John Doe",
        "sales2": "",
        "closer": "Bob Johnson",
        "newused": "Used",
        "year": "2020",
        "make": "Honda",
        "model": "Civic",
        "trade": "No",
        "demo": "Yes",
        "writeup": "Customer wants extended warranty",
        "results": "Sale completed",
        "notes": "Very satisfied customer",
        "datetime": "2023-05-14 10:15:00"
    }
]

# Password utility functions using bcrypt (similar to Crypt::BCrypt in Perl)
def hash_password(password):
    """Create a bcrypt hash of the password"""
    # Using work factor 10 as in the Perl code
    salt = bcrypt.gensalt(rounds=10)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    """Check if the password matches the hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Sample users for the system with bcrypt hashed passwords
USERS = [
    {
        "id": 1,
        "username": "admin",
        "password": hash_password("admin123"),  # Properly hashed with bcrypt
        "full_name": "Administrator",
        "email": "admin@example.com",
        "is_admin": True,
        "is_active": True
    },
    {
        "id": 2,
        "username": "user",
        "password": hash_password("password"),  # Properly hashed with bcrypt
        "full_name": "Regular User",
        "email": "user@example.com",
        "is_admin": False,
        "is_active": True
    }
]

# Function to register a new user
def register_user(username, password, full_name, email):
    # Check if username already exists
    for user in USERS:
        if user["username"] == username:
            return False, "Username already exists"
    
    # Create new user with hashed password
    new_user = {
        "id": len(USERS) + 1,
        "username": username,
        "password": hash_password(password),  # Properly hashed with bcrypt
        "full_name": full_name,
        "email": email,
        "is_admin": False,
        "is_active": True
    }
    
    # Add to users list
    USERS.append(new_user)
    return True, "User registered successfully"

# HTML templates for the demo
HTML_HEADER = """<!DOCTYPE html>
<html lang="en" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Customer Logging System Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bs-primary-rgb: 13, 110, 253;
            --bs-body-bg-dark: #212529;
            --bs-body-color-dark: #f8f9fa;
            --bs-card-bg-dark: #343a40;
            --bs-dark-border-subtle: #495057;
        }
        
        body {
            padding-top: 56px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        
        .main-container {
            flex: 1;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        .footer {
            margin-top: auto;
        }
        
        .card {
            border-radius: 0.5rem;
            margin-bottom: 1.5rem;
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        
        /* Dark mode styles */
        [data-bs-theme="dark"] {
            color-scheme: dark;
        }
        
        [data-bs-theme="dark"] .card {
            --bs-card-bg: var(--bs-card-bg-dark);
            --bs-card-border-color: var(--bs-dark-border-subtle);
        }
        
        [data-bs-theme="dark"] .table {
            --bs-table-bg: var(--bs-card-bg-dark);
            --bs-table-border-color: var(--bs-dark-border-subtle);
        }
        
        [data-bs-theme="dark"] .bg-light {
            background-color: #343a40 !important;
        }
        
        [data-bs-theme="dark"] .text-muted {
            color: #adb5bd !important;
        }
        
        /* Toggle switch for dark mode */
        .mode-switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }
        
        .mode-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .mode-slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }
        
        .mode-slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        
        input:checked + .mode-slider {
            background-color: #6c757d;
        }
        
        input:checked + .mode-slider:before {
            transform: translateX(26px);
        }
        
        .dark-mode-label {
            display: flex;
            align-items: center;
            margin-bottom: 0;
        }
        
        .dark-mode-label span {
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <!-- Top Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
        <div class="container">
            <a class="navbar-brand" href="/">Customer Logging System</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/"><i class="fas fa-home"></i> Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/customers"><i class="fas fa-users"></i> Customers</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/add-customer"><i class="fas fa-user-plus"></i> Add Customer</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/search"><i class="fas fa-search"></i> Search</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/calendar"><i class="fas fa-calendar-alt"></i> Calendar</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/users"><i class="fas fa-user-cog"></i> Users</a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item me-2">
                        <label class="dark-mode-label mt-2">
                            <span class="text-white"><i class="fas fa-moon"></i></span>
                            <label class="mode-switch">
                                <input type="checkbox" id="darkModeToggle">
                                <span class="mode-slider"></span>
                            </label>
                        </label>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user-circle"></i> admin
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="/logout"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container main-container">
"""

HTML_FOOTER = """
    </div>

    <!-- Footer -->
    <footer class="footer mt-auto py-3 bg-light">
        <div class="container text-center">
            <span class="text-muted">&copy; 2023 Customer Logging System. All rights reserved.</span>
        </div>
    </footer>

    <!-- Bootstrap 5 JS Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    
    <!-- Dark Mode Toggle Script -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Check for saved dark mode preference or default to system preference
            const darkModeToggle = document.getElementById('darkModeToggle');
            const htmlElement = document.documentElement;
            
            // Check if user has a saved preference
            const savedTheme = localStorage.getItem('theme');
            
            if (savedTheme) {
                htmlElement.setAttribute('data-bs-theme', savedTheme);
                darkModeToggle.checked = savedTheme === 'dark';
            } else {
                // Default to system preference
                const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
                if (prefersDarkMode) {
                    htmlElement.setAttribute('data-bs-theme', 'dark');
                    darkModeToggle.checked = true;
                }
            }
            
            // Toggle dark mode when switch is clicked
            darkModeToggle.addEventListener('change', function() {
                if (this.checked) {
                    htmlElement.setAttribute('data-bs-theme', 'dark');
                    localStorage.setItem('theme', 'dark');
                } else {
                    htmlElement.setAttribute('data-bs-theme', 'light');
                    localStorage.setItem('theme', 'light');
                }
            });
        });
    </script>
</body>
</html>
"""

LOGIN_PAGE = """<!DOCTYPE html>
<html lang="en" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Login - Customer Logging System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bs-body-bg-dark: #212529;
            --bs-body-color-dark: #f8f9fa;
            --bs-card-bg-dark: #343a40;
            --bs-dark-border-subtle: #495057;
        }
        
        body {
            display: flex;
            align-items: center;
            padding-top: 40px;
            padding-bottom: 40px;
            background-color: #f5f5f5;
            height: 100vh;
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        
        [data-bs-theme="dark"] body {
            background-color: var(--bs-body-bg-dark);
            color: var(--bs-body-color-dark);
        }
        
        [data-bs-theme="dark"] .card {
            --bs-card-bg: var(--bs-card-bg-dark);
            --bs-card-border-color: var(--bs-dark-border-subtle);
        }
        
        [data-bs-theme="dark"] .text-muted {
            color: #adb5bd !important;
        }
        
        .form-signin {
            width: 100%;
            max-width: 420px;
            padding: 15px;
            margin: auto;
        }
        
        /* Toggle switch for dark mode */
        .mode-switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }
        
        .mode-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .mode-slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }
        
        .mode-slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        
        input:checked + .mode-slider {
            background-color: #6c757d;
        }
        
        input:checked + .mode-slider:before {
            transform: translateX(26px);
        }
        
        .dark-mode-label {
            display: flex;
            align-items: center;
            margin-bottom: 0;
        }
        
        .dark-mode-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
        }
    </style>
</head>
<body>
    <div class="dark-mode-toggle">
        <label class="dark-mode-label">
            <span><i class="fas fa-moon"></i></span>
            <label class="mode-switch">
                <input type="checkbox" id="darkModeToggle">
                <span class="mode-slider"></span>
            </label>
        </label>
    </div>

    <div class="container">
        <main class="form-signin">
            <div class="card shadow-sm">
                <div class="card-body p-4">
                    <div class="text-center mb-4">
                        <h2 class="mb-3">Customer Logging System</h2>
                        <p class="text-muted">Please sign in to access the system</p>
                    </div>

                    <div class="alert alert-info" role="alert">
                        <i class="fas fa-info-circle"></i> Demo login credentials: <br>
                        Username: <strong>admin</strong> <br>
                        Password: <strong>admin123</strong>
                    </div>

                    <ul class="nav nav-tabs mb-3" id="loginRegisterTabs" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="login-tab" data-bs-toggle="tab" data-bs-target="#login-tab-pane" type="button" role="tab" aria-controls="login-tab-pane" aria-selected="true">Login</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="register-tab" data-bs-toggle="tab" data-bs-target="#register-tab-pane" type="button" role="tab" aria-controls="register-tab-pane" aria-selected="false">Register</button>
                        </li>
                    </ul>
                    
                    <div class="tab-content" id="loginRegisterTabsContent">
                        <div class="tab-pane fade show active" id="login-tab-pane" role="tabpanel" aria-labelledby="login-tab" tabindex="0">
                            <form method="post" action="/login">
                                <div class="mb-3">
                                    <label for="username" class="form-label">Username</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-user"></i></span>
                                        <input type="text" class="form-control" id="username" name="username" placeholder="Username" required autofocus>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                        <input type="password" class="form-control" id="password" name="password" placeholder="Password" required>
                                    </div>
                                </div>
                                <div class="d-grid gap-2">
                                    <button class="btn btn-primary btn-lg" type="submit" name="submit" value="1">
                                        <i class="fas fa-sign-in-alt"></i> Sign in
                                    </button>
                                </div>
                            </form>
                        </div>
                        
                        <div class="tab-pane fade" id="register-tab-pane" role="tabpanel" aria-labelledby="register-tab" tabindex="0">
                            <form method="post" action="/register">
                                <div class="mb-3">
                                    <label for="new-username" class="form-label">Username</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-user"></i></span>
                                        <input type="text" class="form-control" id="new-username" name="new-username" placeholder="Choose a username" required>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="display-name" class="form-label">Full Name</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-id-card"></i></span>
                                        <input type="text" class="form-control" id="display-name" name="display-name" placeholder="Your full name" required>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                        <input type="email" class="form-control" id="email" name="email" placeholder="Your email address" required>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="new-password" class="form-label">Password</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                        <input type="password" class="form-control" id="new-password" name="new-password" placeholder="Choose a password" required>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="confirm-password" class="form-label">Confirm Password</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                        <input type="password" class="form-control" id="confirm-password" name="confirm-password" placeholder="Confirm your password" required>
                                    </div>
                                </div>
                                <div class="d-grid gap-2">
                                    <button class="btn btn-success btn-lg" type="submit" name="register" value="1">
                                        <i class="fas fa-user-plus"></i> Create Account
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            <div class="text-center mt-3">
                <p class="text-muted">&copy; 2023 Customer Logging System</p>
            </div>
        </main>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Dark Mode Toggle Script -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Check for saved dark mode preference or default to system preference
            const darkModeToggle = document.getElementById('darkModeToggle');
            const htmlElement = document.documentElement;
            
            // Check if user has a saved preference
            const savedTheme = localStorage.getItem('theme');
            
            if (savedTheme) {
                htmlElement.setAttribute('data-bs-theme', savedTheme);
                darkModeToggle.checked = savedTheme === 'dark';
            } else {
                // Default to system preference
                const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
                if (prefersDarkMode) {
                    htmlElement.setAttribute('data-bs-theme', 'dark');
                    darkModeToggle.checked = true;
                }
            }
            
            // Toggle dark mode when switch is clicked
            darkModeToggle.addEventListener('change', function() {
                if (this.checked) {
                    htmlElement.setAttribute('data-bs-theme', 'dark');
                    localStorage.setItem('theme', 'dark');
                } else {
                    htmlElement.setAttribute('data-bs-theme', 'light');
                    localStorage.setItem('theme', 'light');
                }
            });
        });
    </script>
</body>
</html>
"""

DASHBOARD_PAGE = HTML_HEADER + """
<div class="row mb-4">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body">
                <h1 class="card-title display-6">
                    <i class="fas fa-tachometer-alt"></i> Dashboard
                </h1>
                <p class="text-muted">Welcome to the Customer Logging System, admin!</p>
            </div>
        </div>
    </div>
</div>

<div class="row mb-4">
    <!-- Summary Stats -->
    <div class="col-md-8">
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card shadow-sm border-primary h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h5 class="card-title">Total Customers</h5>
                                <h2 class="display-4">2</h2>
                            </div>
                            <div class="display-4 text-primary">
                                <i class="fas fa-users"></i>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer bg-transparent border-primary">
                        <a href="/customers" class="text-decoration-none">View all customers <i class="fas fa-arrow-right"></i></a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card shadow-sm border-success h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h5 class="card-title">Today's Customers</h5>
                                <h2 class="display-4">1</h2>
                            </div>
                            <div class="display-4 text-success">
                                <i class="fas fa-user-plus"></i>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer bg-transparent border-success">
                        <a href="/add-customer" class="text-decoration-none">Add new customer <i class="fas fa-arrow-right"></i></a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12 mb-4">
                <div class="card shadow-sm">
                    <div class="card-header bg-light">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0"><i class="fas fa-chart-line"></i> Customer Analytics</h5>
                            <a href="/search" class="btn btn-sm btn-primary">
                                <i class="fas fa-search"></i> Search
                            </a>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Time Period</th>
                                        <th>New</th>
                                        <th>Used</th>
                                        <th>Write Up</th>
                                        <th>Demo</th>
                                        <th>Results</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Today</td>
                                        <td>1</td>
                                        <td>0</td>
                                        <td>1</td>
                                        <td>1</td>
                                        <td>1</td>
                                    </tr>
                                    <tr>
                                        <td>This Month</td>
                                        <td>3</td>
                                        <td>2</td>
                                        <td>4</td>
                                        <td>2</td>
                                        <td>5</td>
                                    </tr>
                                    <tr>
                                        <td>Last Month</td>
                                        <td>5</td>
                                        <td>7</td>
                                        <td>8</td>
                                        <td>3</td>
                                        <td>10</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Calendar and Recent Customers -->
    <div class="col-md-4">
        <div class="card shadow-sm mb-4">
            <div class="card-header bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-calendar-alt"></i> Calendar</h5>
                    <a href="/calendar" class="btn btn-sm btn-primary">Full Calendar</a>
                </div>
            </div>
            <div class="card-body">
                <div class="text-center mb-3">
                    <h6 class="text-center">May 2023</h6>
                    <p>Calendar functionality shows customer activity by date</p>
                </div>
                <div class="text-center">
                    <a href="/calendar" class="btn btn-outline-primary btn-sm">
                        View monthly activity
                    </a>
                </div>
            </div>
        </div>
        
        <div class="card shadow-sm">
            <div class="card-header bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-history"></i> Recent Customers</h5>
                    <a href="/customers" class="btn btn-sm btn-primary">View All</a>
                </div>
            </div>
            <div class="card-body p-0">
                <div class="list-group list-group-flush">
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">John Doe</h6>
                            <small class="text-muted">2023-05-15</small>
                        </div>
                        <p class="mb-1">Toyota Camry</p>
                        <small class="text-muted">Sales: Jane Smith</small>
                    </div>
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">Jane Smith</h6>
                            <small class="text-muted">2023-05-14</small>
                        </div>
                        <p class="mb-1">Honda Civic</p>
                        <small class="text-muted">Sales: John Doe</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
""" + HTML_FOOTER

CUSTOMERS_PAGE = HTML_HEADER + """
<div class="row mb-4">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <h1 class="card-title">
                        <i class="fas fa-users"></i> Customer List
                    </h1>
                    <div>
                        <a href="/search" class="btn btn-primary me-2">
                            <i class="fas fa-search"></i> Search
                        </a>
                        <a href="/add-customer" class="btn btn-success">
                            <i class="fas fa-user-plus"></i> Add Customer
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover table-striped">
                        <thead class="table-light">
                            <tr>
                                <th>Name</th>
                                <th>Phone</th>
                                <th>Email</th>
                                <th>Vehicle</th>
                                <th>Sales Person</th>
                                <th>Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>John Doe</td>
                                <td>(555) 123-4567</td>
                                <td>john@example.com</td>
                                <td>2023 Toyota Camry</td>
                                <td>Jane Smith</td>
                                <td>2023-05-15</td>
                                <td>
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/edit-customer/1" class="btn btn-outline-primary" title="Edit">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger" title="Delete">
                                            <i class="fas fa-trash-alt"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td>Jane Smith</td>
                                <td>(555) 987-6543</td>
                                <td>jane@example.com</td>
                                <td>2020 Honda Civic</td>
                                <td>John Doe</td>
                                <td>2023-05-14</td>
                                <td>
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/edit-customer/2" class="btn btn-outline-primary" title="Edit">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger" title="Delete">
                                            <i class="fas fa-trash-alt"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
""" + HTML_FOOTER

SEARCH_PAGE = HTML_HEADER + """
<div class="row mb-4">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body">
                <h1 class="card-title">
                    <i class="fas fa-search"></i> Search Customers
                </h1>
                <p class="text-muted">Search for customers by name, phone, email, or other criteria</p>
            </div>
        </div>
    </div>
</div>

<div class="row mb-4">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body">
                <form method="get" action="/search" class="row g-3">
                    <div class="col-md-6 col-lg-8">
                        <div class="input-group">
                            <span class="input-group-text"><i class="fas fa-search"></i></span>
                            <input type="text" class="form-control form-control-lg" placeholder="Search..." name="search_term" required>
                        </div>
                    </div>
                    <div class="col-md-4 col-lg-2">
                        <select class="form-select form-select-lg" name="search_field">
                            <option value="all" selected>All Fields</option>
                            <option value="name">Name</option>
                            <option value="phone">Phone</option>
                            <option value="email">Email</option>
                            <option value="city">City</option>
                        </select>
                    </div>
                    <div class="col-md-2 col-lg-2">
                        <button type="submit" class="btn btn-primary btn-lg w-100">Search</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-header bg-light">
                <h5 class="mb-0">
                    <i class="fas fa-info-circle"></i> Search Information
                </h5>
            </div>
            <div class="card-body text-center py-5">
                <div class="text-muted">
                    <i class="fas fa-search fa-3x mb-3"></i>
                    <p>Enter search terms above to find customers</p>
                    <p class="small">You can search by name, phone, email, city, or across all fields</p>
                </div>
            </div>
        </div>
    </div>
</div>
""" + HTML_FOOTER

ADD_CUSTOMER_PAGE = HTML_HEADER + """
<div class="row mb-4">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body">
                <h1 class="card-title">
                    <i class="fas fa-user-plus"></i> Add New Customer
                </h1>
                <p class="text-muted">Create a new customer record</p>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body">
                <form method="post" action="/add-customer">
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <h4>Customer Information</h4>
                            <div class="card card-body bg-light mb-3">
                                <div class="mb-3">
                                    <label for="user" class="form-label">User <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="user" name="user" value="admin" required>
                                </div>
                                <div class="mb-3">
                                    <label for="name" class="form-label">Customer Name <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="name" name="name" required>
                                    <div class="form-text text-muted">This field will be encrypted</div>
                                </div>
                                <div class="mb-3">
                                    <label for="phone" class="form-label">Phone Number <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="phone" name="phone" required>
                                    <div class="form-text text-muted">This field will be encrypted</div>
                                </div>
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email Address</label>
                                    <input type="email" class="form-control" id="email" name="email">
                                </div>
                                <div class="mb-3">
                                    <label for="city" class="form-label">City</label>
                                    <input type="text" class="form-control" id="city" name="city">
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <h4>Sales Details</h4>
                            <div class="card card-body bg-light mb-3">
                                <div class="mb-3">
                                    <label for="stackno" class="form-label">Stack Number</label>
                                    <input type="text" class="form-control" id="stackno" name="stackno">
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="sales1" class="form-label">Sales Person 1</label>
                                        <input type="text" class="form-control" id="sales1" name="sales1">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label for="sales2" class="form-label">Sales Person 2</label>
                                        <input type="text" class="form-control" id="sales2" name="sales2">
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="closer" class="form-label">Closer</label>
                                    <input type="text" class="form-control" id="closer" name="closer">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Type</label>
                                    <select class="form-select" name="newused">
                                        <option value="New" selected>New</option>
                                        <option value="Used">Used</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <h4>Vehicle Information</h4>
                            <div class="card card-body bg-light mb-3">
                                <div class="row">
                                    <div class="col-md-4 mb-3">
                                        <label for="year" class="form-label">Year</label>
                                        <input type="text" class="form-control" id="year" name="year">
                                    </div>
                                    <div class="col-md-4 mb-3">
                                        <label for="make" class="form-label">Make</label>
                                        <input type="text" class="form-control" id="make" name="make">
                                    </div>
                                    <div class="col-md-4 mb-3">
                                        <label for="model" class="form-label">Model</label>
                                        <input type="text" class="form-control" id="model" name="model">
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="trade" class="form-label">Trade</label>
                                    <input type="text" class="form-control" id="trade" name="trade">
                                </div>
                                <div class="mb-3">
                                    <label for="demo" class="form-label">Demo</label>
                                    <select class="form-select" name="demo">
                                        <option value="Yes">Yes</option>
                                        <option value="No" selected>No</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <h4>Additional Information</h4>
                            <div class="card card-body bg-light mb-3">
                                <div class="mb-3">
                                    <label for="writeup" class="form-label">Write-up</label>
                                    <textarea class="form-control" id="writeup" name="writeup" rows="2"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="results" class="form-label">Results</label>
                                    <textarea class="form-control" id="results" name="results" rows="2"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="notes" class="form-label">Notes</label>
                                    <textarea class="form-control" id="notes" name="notes" rows="3"></textarea>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="d-flex justify-content-between">
                        <a href="/customers" class="btn btn-secondary">
                            <i class="fas fa-arrow-left"></i> Back to List
                        </a>
                        <button type="submit" name="submit" value="1" class="btn btn-primary">
                            <i class="fas fa-user-plus"></i> Add Customer
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
""" + HTML_FOOTER

CALENDAR_PAGE = HTML_HEADER + """
<div class="row mb-4">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body">
                <h1 class="card-title">
                    <i class="fas fa-calendar-alt"></i> Customer Calendar
                </h1>
                <p class="text-muted">View customer activity by date</p>
            </div>
        </div>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-8">
        <div class="card shadow-sm">
            <div class="card-header bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h5 class="mb-0">May 2023</h5>
                    </div>
                    <div class="btn-group">
                        <a href="/calendar?month=4&year=2023" class="btn btn-outline-primary">
                            <i class="fas fa-chevron-left"></i>
                        </a>
                        <a href="/calendar" class="btn btn-outline-primary">Today</a>
                        <a href="/calendar?month=6&year=2023" class="btn btn-outline-primary">
                            <i class="fas fa-chevron-right"></i>
                        </a>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <style>
                    .calendar-table td {
                        height: 60px;
                        vertical-align: top;
                        text-align: center;
                        width: 14.28%;
                        position: relative;
                        padding: 5px;
                    }
                    .date-cell {
                        display: block;
                        height: 100%;
                        text-decoration: none;
                        color: inherit;
                        border-radius: 5px;
                        transition: background-color 0.2s;
                        position: relative;
                    }
                    .date-cell:hover {
                        background-color: #e9ecef;
                    }
                    .date-number {
                        position: absolute;
                        top: 5px;
                        right: 5px;
                        font-weight: bold;
                    }
                    .date-dot {
                        width: 6px;
                        height: 6px;
                        border-radius: 50%;
                        background-color: #007bff;
                        position: absolute;
                        bottom: 5px;
                        left: 50%;
                        transform: translateX(-50%);
                    }
                    .current-date {
                        background-color: #e2f0ff;
                        border: 2px solid #007bff;
                    }
                    .selected-date {
                        background-color: #e9ecef;
                        border: 2px solid #6c757d;
                    }
                    .has-records {
                        font-weight: 500;
                    }
                </style>
                <table class="table table-bordered calendar-table">
                    <thead>
                        <tr>
                            <th>Sun</th>
                            <th>Mon</th>
                            <th>Tue</th>
                            <th>Wed</th>
                            <th>Thu</th>
                            <th>Fri</th>
                            <th>Sat</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td></td>
                            <td>
                                <a href="/calendar?day=1&month=5&year=2023" class="date-cell">
                                    <span class="date-number">1</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=2&month=5&year=2023" class="date-cell">
                                    <span class="date-number">2</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=3&month=5&year=2023" class="date-cell">
                                    <span class="date-number">3</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=4&month=5&year=2023" class="date-cell">
                                    <span class="date-number">4</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=5&month=5&year=2023" class="date-cell">
                                    <span class="date-number">5</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=6&month=5&year=2023" class="date-cell">
                                    <span class="date-number">6</span>
                                </a>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <a href="/calendar?day=7&month=5&year=2023" class="date-cell">
                                    <span class="date-number">7</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=8&month=5&year=2023" class="date-cell">
                                    <span class="date-number">8</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=9&month=5&year=2023" class="date-cell">
                                    <span class="date-number">9</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=10&month=5&year=2023" class="date-cell">
                                    <span class="date-number">10</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=11&month=5&year=2023" class="date-cell">
                                    <span class="date-number">11</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=12&month=5&year=2023" class="date-cell">
                                    <span class="date-number">12</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=13&month=5&year=2023" class="date-cell">
                                    <span class="date-number">13</span>
                                </a>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <a href="/calendar?day=14&month=5&year=2023" class="date-cell has-records">
                                    <span class="date-number">14</span>
                                    <span class="date-dot"></span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=15&month=5&year=2023" class="date-cell selected-date has-records">
                                    <span class="date-number">15</span>
                                    <span class="date-dot"></span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=16&month=5&year=2023" class="date-cell">
                                    <span class="date-number">16</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=17&month=5&year=2023" class="date-cell">
                                    <span class="date-number">17</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=18&month=5&year=2023" class="date-cell">
                                    <span class="date-number">18</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=19&month=5&year=2023" class="date-cell">
                                    <span class="date-number">19</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=20&month=5&year=2023" class="date-cell current-date">
                                    <span class="date-number">20</span>
                                </a>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <a href="/calendar?day=21&month=5&year=2023" class="date-cell">
                                    <span class="date-number">21</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=22&month=5&year=2023" class="date-cell">
                                    <span class="date-number">22</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=23&month=5&year=2023" class="date-cell">
                                    <span class="date-number">23</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=24&month=5&year=2023" class="date-cell">
                                    <span class="date-number">24</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=25&month=5&year=2023" class="date-cell">
                                    <span class="date-number">25</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=26&month=5&year=2023" class="date-cell">
                                    <span class="date-number">26</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=27&month=5&year=2023" class="date-cell">
                                    <span class="date-number">27</span>
                                </a>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <a href="/calendar?day=28&month=5&year=2023" class="date-cell">
                                    <span class="date-number">28</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=29&month=5&year=2023" class="date-cell">
                                    <span class="date-number">29</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=30&month=5&year=2023" class="date-cell">
                                    <span class="date-number">30</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=31&month=5&year=2023" class="date-cell">
                                    <span class="date-number">31</span>
                                </a>
                            </td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card shadow-sm">
            <div class="card-header bg-light">
                <h5 class="mb-0">
                    <i class="fas fa-list"></i> Customers for May 15, 2023
                </h5>
            </div>
            <div class="card-body">
                <div class="list-group list-group-flush">
                    <div class="list-group-item px-0">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">John Doe</h6>
                            <small class="text-muted">14:30</small>
                        </div>
                        <p class="mb-1 small">
                            <i class="fas fa-map-marker-alt text-secondary"></i> New York<br>
                            <i class="fas fa-car text-secondary"></i> Toyota Camry<br>
                            <i class="fas fa-user text-secondary"></i> Jane Smith
                        </p>
                        <div class="mt-2">
                            <button type="button" class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#customerDetailModal">
                                <i class="fas fa-eye"></i> View
                            </button>
                            <a href="/edit-customer/1" class="btn btn-sm btn-outline-secondary">
                                <i class="fas fa-edit"></i> Edit
                            </a>
                        </div>
                    </div>
                </div>
                
                <!-- Customer Detail Modal -->
                <div class="modal fade" id="customerDetailModal" tabindex="-1" aria-labelledby="customerDetailModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="customerDetailModalLabel">John Doe - Customer Details</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Customer Information</h6>
                                        <dl class="row mb-0">
                                            <dt class="col-sm-4">Name:</dt>
                                            <dd class="col-sm-8">John Doe</dd>
                                            
                                            <dt class="col-sm-4">Phone:</dt>
                                            <dd class="col-sm-8">(555) 123-4567</dd>
                                            
                                            <dt class="col-sm-4">Email:</dt>
                                            <dd class="col-sm-8">john@example.com</dd>
                                            
                                            <dt class="col-sm-4">City:</dt>
                                            <dd class="col-sm-8">New York</dd>
                                        </dl>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Vehicle Information</h6>
                                        <dl class="row mb-0">
                                            <dt class="col-sm-4">Year:</dt>
                                            <dd class="col-sm-8">2023</dd>
                                            
                                            <dt class="col-sm-4">Make:</dt>
                                            <dd class="col-sm-8">Toyota</dd>
                                            
                                            <dt class="col-sm-4">Model:</dt>
                                            <dd class="col-sm-8">Camry</dd>
                                            
                                            <dt class="col-sm-4">Type:</dt>
                                            <dd class="col-sm-8">New</dd>
                                        </dl>
                                    </div>
                                </div>
                                <hr>
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Sales Information</h6>
                                        <dl class="row mb-0">
                                            <dt class="col-sm-4">Sales 1:</dt>
                                            <dd class="col-sm-8">Jane Smith</dd>
                                            
                                            <dt class="col-sm-4">Sales 2:</dt>
                                            <dd class="col-sm-8">Bob Johnson</dd>
                                            
                                            <dt class="col-sm-4">Closer:</dt>
                                            <dd class="col-sm-8">Alice Brown</dd>
                                            
                                            <dt class="col-sm-4">Stack #:</dt>
                                            <dd class="col-sm-8">A123</dd>
                                        </dl>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Additional Information</h6>
                                        <dl class="row mb-0">
                                            <dt class="col-sm-4">Trade:</dt>
                                            <dd class="col-sm-8">Yes</dd>
                                            
                                            <dt class="col-sm-4">Demo:</dt>
                                            <dd class="col-sm-8">No</dd>
                                            
                                            <dt class="col-sm-4">Date/Time:</dt>
                                            <dd class="col-sm-8">2023-05-15 14:30:00</dd>
                                        </dl>
                                    </div>
                                </div>
                                <hr>
                                <div class="row">
                                    <div class="col-12">
                                        <h6>Notes</h6>
                                        <p>Customer is interested in financing options</p>
                                        
                                        <h6>Results</h6>
                                        <p>Pending final approval</p>
                                        
                                        <h6>Write-up</h6>
                                        <p>Follow up next week</p>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                <a href="/edit-customer/1" class="btn btn-primary">Edit Customer</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card shadow-sm mt-4">
            <div class="card-header bg-light">
                <h5 class="mb-0">
                    <i class="fas fa-info-circle"></i> Calendar Legend
                </h5>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <div class="d-flex align-items-center mb-2">
                        <div class="me-2 p-2" style="background-color: #e2f0ff; border: 2px solid #007bff; width: 30px; height: 30px; border-radius: 5px;"></div>
                        <div>Current day (May 20)</div>
                    </div>
                    <div class="d-flex align-items-center mb-2">
                        <div class="me-2 p-2" style="background-color: #e9ecef; border: 2px solid #6c757d; width: 30px; height: 30px; border-radius: 5px;"></div>
                        <div>Selected day (May 15)</div>
                    </div>
                    <div class="d-flex align-items-center">
                        <div class="me-2 p-2 position-relative" style="width: 30px; height: 30px; border-radius: 5px; border: 1px solid #dee2e6;">
                            <div style="width: 6px; height: 6px; border-radius: 50%; background-color: #007bff; position: absolute; bottom: 2px; left: 12px;"></div>
                        </div>
                        <div>Day with customer records</div>
                    </div>
                </div>
                <div class="text-center mt-4">
                    <a href="/calendar" class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-calendar-alt"></i> View Current Month
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
""" + HTML_FOOTER

USERS_PAGE = HTML_HEADER + """
<div class="row mb-4">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <h1 class="card-title">
                        <i class="fas fa-users-cog"></i> User Management
                    </h1>
                    <a href="/add-user" class="btn btn-success">
                        <i class="fas fa-user-plus"></i> Add User
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover table-striped">
                        <thead class="table-light">
                            <tr>
                                <th>Username</th>
                                <th>Full Name</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>admin</td>
                                <td>Administrator</td>
                                <td>admin@example.com</td>
                                <td>
                                    <span class="badge bg-danger">Administrator</span>
                                </td>
                                <td>
                                    <span class="badge bg-success">Active</span>
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/edit-user/1" class="btn btn-outline-primary" title="Edit">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger" disabled title="Cannot delete your own account">
                                            <i class="fas fa-trash-alt"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td>user</td>
                                <td>Regular User</td>
                                <td>user@example.com</td>
                                <td>
                                    <span class="badge bg-primary">Standard User</span>
                                </td>
                                <td>
                                    <span class="badge bg-success">Active</span>
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/edit-user/2" class="btn btn-outline-primary" title="Edit">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger" title="Delete">
                                            <i class="fas fa-trash-alt"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
""" + HTML_FOOTER

# Demo information page
INFO_PAGE = HTML_HEADER + """
<div class="row mb-4">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body">
                <h1 class="card-title">
                    <i class="fas fa-info-circle"></i> Customer Logging System Demo
                </h1>
                <p class="text-muted">This is a demo version of the Perl-based customer logging application</p>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0">About This Application</h4>
            </div>
            <div class="card-body">
                <p>This is a demonstration version of a Customer Logging System built with the following technologies:</p>
                
                <h5>Backend Technology</h5>
                <ul>
                    <li>Perl with CGI for request handling</li>
                    <li>MariaDB/MySQL for database storage</li>
                    <li>Template Toolkit for view templating</li>
                    <li>CGI::Session for session management</li>
                    <li>Crypt::BCrypt for secure password hashing</li>
                    <li>AES-256 encryption for sensitive customer data</li>
                </ul>
                
                <h5>Frontend Technology</h5>
                <ul>
                    <li>Bootstrap 5 for responsive UI</li>
                    <li>Font Awesome 5 for icons</li>
                    <li>jQuery for JavaScript enhancements</li>
                </ul>
                
                <h5>Features</h5>
                <ul>
                    <li>User authentication with secure password hashing</li>
                    <li>User management (add, edit, delete users)</li>
                    <li>Customer management (add, edit, delete customer records)</li>
                    <li>Encryption of sensitive customer data (name, phone)</li>
                    <li>Searchable customer database with multiple field options</li>
                    <li>Calendar view to see customers by date</li>
                    <li>Dashboard with summary statistics</li>
                    <li>Responsive design works on desktop and mobile devices</li>
                </ul>
                
                <div class="alert alert-info mt-3">
                    <h5><i class="fas fa-lightbulb"></i> Demo Notes</h5>
                    <p>This demo shows the user interface and structure of the application. In a production environment:</p>
                    <ul>
                        <li>All data would be stored in a MariaDB/MySQL database</li>
                        <li>Passwords would be securely hashed with Crypt::BCrypt</li>
                        <li>Sensitive customer information would be encrypted</li>
                        <li>All pages would be generated dynamically from database content</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
""" + HTML_FOOTER

class CustomerLoggingHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Default to root path
        if path == '/':
            self._send_response(DASHBOARD_PAGE)
            return
            
        # Handle login page
        elif path == '/login':
            self._send_response(LOGIN_PAGE)
            return
            
        # Handle dashboard
        elif path == '/dashboard':
            self._send_response(DASHBOARD_PAGE)
            return
            
        # Handle customers list
        elif path == '/customers':
            self._send_response(CUSTOMERS_PAGE)
            return
            
        # Handle search page
        elif path == '/search':
            self._send_response(SEARCH_PAGE)
            return
            
        # Handle add customer page
        elif path == '/add-customer':
            self._send_response(ADD_CUSTOMER_PAGE)
            return
            
        # Handle calendar page
        elif path == '/calendar':
            self._send_response(CALENDAR_PAGE)
            return
            
        # Handle users page
        elif path == '/users':
            self._send_response(USERS_PAGE)
            return
            
        # Handle info page
        elif path == '/info':
            self._send_response(INFO_PAGE)
            return
            
        # Handle logout (redirect to login)
        elif path == '/logout':
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
            
        # Default response for unknown paths
        else:
            self._send_response(INFO_PAGE)
            return
            
    def do_POST(self):
        # Handle login form submission
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            
            # Check credentials against USERS list with secure password verification
            user_authenticated = False
            for user in USERS:
                if user["username"] == username and verify_password(password, user["password"]):
                    user_authenticated = True
                    break
                    
            if user_authenticated:
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self._send_response(LOGIN_PAGE)
                
        # Handle user registration
        elif self.path == '/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            
            new_username = params.get('new-username', [''])[0]
            display_name = params.get('display-name', [''])[0]
            email = params.get('email', [''])[0]
            new_password = params.get('new-password', [''])[0]
            confirm_password = params.get('confirm-password', [''])[0]
            
            # Validate form data
            if not new_username or not display_name or not email or not new_password:
                # Missing required fields
                self._send_response(LOGIN_PAGE + """
                <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.getElementById('register-tab').click();
                        alert('Please fill in all required fields');
                    });
                </script>
                """)
            elif new_password != confirm_password:
                # Passwords don't match
                self._send_response(LOGIN_PAGE + """
                <script>
                    document.addEventListener('DOMContentLoaded', function() {
                        document.getElementById('register-tab').click();
                        alert('Passwords do not match');
                    });
                </script>
                """)
            else:
                # Register the new user
                success, message = register_user(new_username, new_password, display_name, email)
                
                if success:
                    # Registration successful, redirect to login
                    self._send_response(LOGIN_PAGE + """
                    <script>
                        document.addEventListener('DOMContentLoaded', function() {
                            alert('Registration successful! Please log in with your new credentials.');
                        });
                    </script>
                    """)
                else:
                    # Registration failed
                    self._send_response(LOGIN_PAGE + f"""
                    <script>
                        document.addEventListener('DOMContentLoaded', function() {{
                            document.getElementById('register-tab').click();
                            alert('{message}');
                        }});
                    </script>
                    """)
        else:
            # For other POST requests, just redirect back to the dashboard
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            
    def _send_response(self, content):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

def run(server_class=http.server.HTTPServer, handler_class=CustomerLoggingHandler, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting Customer Logging System demo server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()