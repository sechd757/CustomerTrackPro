#!/usr/bin/env python3
"""
Simple Python server to demonstrate the Customer Logging System
This serves as a demo of the Perl application structure
"""

import http.server
import socketserver
import os
import json
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

# Sample users for the system
USERS = [
    {
        "id": 1,
        "username": "admin",
        "password": "admin123",  # In real app, this would be hashed
        "full_name": "Administrator",
        "email": "admin@example.com",
        "is_admin": True,
        "is_active": True
    },
    {
        "id": 2,
        "username": "user",
        "password": "password",  # In real app, this would be hashed
        "full_name": "Regular User",
        "email": "user@example.com",
        "is_admin": False,
        "is_active": True
    }
]

# HTML templates for the demo
HTML_HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Customer Logging System Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        body {
            padding-top: 56px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
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
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</body>
</html>
"""

LOGIN_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Login - Customer Logging System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        body {
            display: flex;
            align-items: center;
            padding-top: 40px;
            padding-bottom: 40px;
            background-color: #f5f5f5;
            height: 100vh;
        }
        .form-signin {
            width: 100%;
            max-width: 420px;
            padding: 15px;
            margin: auto;
        }
    </style>
</head>
<body>
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
            </div>
            <div class="text-center mt-3">
                <p class="text-muted">&copy; 2023 Customer Logging System</p>
            </div>
        </main>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
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
                                        <th>Type</th>
                                        <th>New</th>
                                        <th>Used</th>
                                        <th>Demos</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>This Month</td>
                                        <td>1</td>
                                        <td>1</td>
                                        <td>1</td>
                                    </tr>
                                    <tr>
                                        <td>Last Month</td>
                                        <td>0</td>
                                        <td>0</td>
                                        <td>0</td>
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
                    }
                    .date-cell:hover {
                        background-color: #e9ecef;
                    }
                    .date-number {
                        font-weight: bold;
                        position: absolute;
                        top: 5px;
                        right: 5px;
                    }
                    .customer-badge {
                        position: absolute;
                        bottom: 5px;
                        left: 50%;
                        transform: translateX(-50%);
                        background-color: #007bff;
                        color: white;
                        border-radius: 50%;
                        width: 24px;
                        height: 24px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 0.75rem;
                    }
                    .current-date {
                        background-color: #e2f0ff;
                        border: 2px solid #007bff;
                    }
                    .has-records {
                        background-color: #f8f9fa;
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
                                    <span class="customer-badge">1</span>
                                </a>
                            </td>
                            <td>
                                <a href="/calendar?day=15&month=5&year=2023" class="date-cell has-records">
                                    <span class="date-number">15</span>
                                    <span class="customer-badge">1</span>
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
                    <i class="fas fa-info-circle"></i> Calendar Information
                </h5>
            </div>
            <div class="card-body">
                <div class="text-center py-4">
                    <div class="text-muted">
                        <i class="fas fa-calendar-alt fa-3x mb-3"></i>
                        <p>Select a date to view customers added on that day</p>
                        <p class="small">Dates with customer records are highlighted with a badge showing the count</p>
                        <div class="mt-4">
                            <div class="d-flex align-items-center justify-content-center mb-2">
                                <div class="me-2" style="width: 20px; height: 20px; background-color: #e2f0ff; border: 2px solid #007bff;"></div>
                                <div>Current date</div>
                            </div>
                            <div class="d-flex align-items-center justify-content-center">
                                <div class="me-2" style="width: 20px; height: 20px; background-color: #f8f9fa;"></div>
                                <div>Date with customer records</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card shadow-sm mt-4">
            <div class="card-header bg-light">
                <h5 class="mb-0">
                    <i class="fas fa-user-clock"></i> Recent Activity
                </h5>
            </div>
            <div class="card-body">
                <div class="list-group list-group-flush">
                    <div class="list-group-item px-0">
                        <div class="d-flex justify-content-between">
                            <h6 class="mb-1">May 15, 2023</h6>
                            <span class="badge bg-primary">1 customer</span>
                        </div>
                        <p class="mb-1">John Doe - Toyota Camry</p>
                    </div>
                    <div class="list-group-item px-0">
                        <div class="d-flex justify-content-between">
                            <h6 class="mb-1">May 14, 2023</h6>
                            <span class="badge bg-primary">1 customer</span>
                        </div>
                        <p class="mb-1">Jane Smith - Honda Civic</p>
                    </div>
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
            
            # Simple login check
            if username == 'admin' and password == 'admin123':
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self._send_response(LOGIN_PAGE)
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