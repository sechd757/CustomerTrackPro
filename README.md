# Customer Logging System

A comprehensive Perl-based application for tracking customer information with advanced security features.

## Features

- **Secure Authentication**: User accounts with bcrypt password hashing
- **Customer Management**: Add, edit, view, and search customer records
- **Data Encryption**: Sensitive customer data (names, phone numbers) are encrypted
- **Searchable Encryption**: Search through encrypted data securely
- **Calendar View**: Track customers by date with visual calendar
- **Responsive UI**: Bootstrap-based interface that works on all devices
- **Dark Mode**: Toggle between light and dark themes for comfortable viewing
- **User Management**: Create and manage system users with role-based permissions
- **Analytics Dashboard**: Quick overview of customer statistics

## System Requirements

- Perl 5.14 or higher
- MySQL/MariaDB database
- Web server with CGI support (Apache or Nginx)

## Quick Start

### Installation

1. Clone the repository to your web server directory
2. Run the installation script:

```bash
sudo ./install.sh
```

3. Configure the application:

```bash
perl setup.pl
```

4. For development mode, run:

```bash
perl server.pl
```

### Default Login

- Username: `admin`
- Password: `admin123`

**Important**: Change the default password immediately after first login!

## Deployment

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Database Management

- **Setup**: Database schema is automatically set up during installation
- **Migrations**: Use `perl migrate.pl` to update database structure
- **Backup**: Use `perl backup.pl` to back up your database

## Application Structure

- **CGI Scripts**: Main entry points (`*.cgi` files)
- **Perl Modules**: Core functionality in `lib/` directory
- **Templates**: UI templates in `templates/` directory
- **SQL**: Database schema and migrations in `sql/` directory
- **Static Assets**: CSS, JavaScript, and images in `static/` directory

## Security Features

- **Password Hashing**: Secure password storage using bcrypt
- **Data Encryption**: AES-CBC encryption for sensitive customer information
- **Searchable Encryption**: Ability to search through encrypted data
- **Session Management**: Secure session handling with timeouts
- **Input Validation**: Comprehensive validation of all user inputs

## Maintenance

### Updates

To update the application:

1. Back up your database:
   ```bash
   perl backup.pl
   ```

2. Pull the latest code

3. Update the database schema if needed:
   ```bash
   perl migrate.pl
   ```

### Configuration

Edit `lib/Config.pm` to change:
- Database connection details
- Encryption keys
- Session parameters

## License

This software is proprietary and confidential.
All rights reserved.

## Support

For support and questions, please contact your system administrator.