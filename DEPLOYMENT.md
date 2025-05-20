# Customer Logging System - Deployment Guide

This guide details how to deploy the Customer Logging System on various environments.

## Prerequisites

- Perl 5.14 or higher
- MySQL/MariaDB database
- Web server with CGI support (Apache or Nginx)

## Required Perl Modules

- CGI
- CGI::Session
- DBI
- DBD::mysql
- Template
- Crypt::BCrypt
- Crypt::Mode::CBC
- Crypt::AuthEnc::GCM
- MIME::Base64
- Crypt::PRNG
- HTTP::Server::Simple::CGI
- JSON

## Deployment Options

### 1. Automated Setup (Recommended)

Run the included setup script to automatically configure the system:

```
perl setup.pl
```

The script will:
- Install required Perl modules
- Create necessary directories and set permissions
- Configure database connection
- Import database schema
- Create admin user
- Generate encryption keys
- Create Apache .htaccess file

### 2. Manual Setup

If you prefer to set up the system manually, follow these steps:

#### A. Install Required Perl Modules

```bash
cpan CGI CGI::Session DBI DBD::mysql Template Crypt::BCrypt Crypt::Mode::CBC Crypt::AuthEnc::GCM MIME::Base64 Crypt::PRNG HTTP::Server::Simple::CGI JSON
```

#### B. Create Required Directories

```bash
mkdir -p sessions logs db
chmod 777 sessions logs
```

#### C. Set CGI Script Permissions

```bash
chmod 755 *.cgi
```

#### D. Database Setup

1. Create a MySQL/MariaDB database:
   ```sql
   CREATE DATABASE customer_log CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. Create a database user:
   ```sql
   CREATE USER 'customer_log_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON customer_log.* TO 'customer_log_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. Import the schema:
   ```bash
   mysql -u customer_log_user -p customer_log < sql/schema.sql
   ```

#### E. Configure Application

1. Edit `lib/Config.pm` with your database details and encryption key:
   ```perl
   our $DB_HOST = 'localhost';
   our $DB_PORT = 3306;
   our $DB_NAME = 'customer_log';
   our $DB_USER = 'customer_log_user';
   our $DB_PASS = 'your_password';
   our $ENCRYPTION_KEY = 'your_32_character_encryption_key';
   ```

#### F. Web Server Configuration

##### Apache

Create a `.htaccess` file in the root directory:
```
Options +ExecCGI
AddHandler cgi-script .cgi
DirectoryIndex index.cgi
RewriteEngine On
RewriteBase /
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.cgi/$1 [QSA,L]
```

Make sure mod_cgi and mod_rewrite are enabled in Apache:
```
a2enmod cgi
a2enmod rewrite
```

##### Nginx

Use Nginx with FastCGI:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/customer_logging_system;
    
    location / {
        index index.cgi;
        try_files $uri $uri/ @cgi;
    }
    
    location @cgi {
        rewrite ^(.*)$ /index.cgi$1 last;
    }
    
    location ~ \.cgi$ {
        gzip off;
        include fastcgi_params;
        fastcgi_pass unix:/var/run/fcgiwrap.socket;
        fastcgi_index index.cgi;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
}
```

You'll need to install `fcgiwrap`:
```
apt-get install fcgiwrap
```

## Running in Development Mode

For development, you can use the built-in HTTP server:

```bash
perl server.pl
```

This will start a server on port 5000. Access the application at http://localhost:5000.

## Post-Deployment Steps

1. Login with the default admin credentials:
   - Username: admin
   - Password: admin123

2. **Change the default admin password immediately!**

3. Create additional users as needed.

## Security Considerations

1. The application uses encryption for sensitive customer data (name, phone).
2. Passwords are securely hashed using bcrypt.
3. For production, always:
   - Use HTTPS
   - Set secure file permissions
   - Change the default encryption key
   - Change the default admin password

## Troubleshooting

- **Permissions Issues**: Ensure the web server has appropriate permissions for sessions and logs directories.
- **Database Connection Errors**: Verify database credentials in Config.pm.
- **Missing Perl Modules**: Install any missing modules using CPAN.
- **CGI Errors**: Check web server error logs for details.

## File Structure Reference

- `*.cgi` - CGI entry points
- `lib/` - Perl modules
- `templates/` - Template files
- `sql/` - Database schema
- `sessions/` - Session storage
- `logs/` - Application logs
- `static/` - Static assets (CSS, JS, images)