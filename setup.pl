#!/usr/bin/perl

use strict;
use warnings;
use CPAN;
use DBI;
use Term::ReadKey;
use File::Copy;
use File::Basename;
use File::Path qw(make_path);
use FindBin qw($Bin);

print "\n";
print "===========================================\n";
print "Customer Logging System - Setup Script\n";
print "===========================================\n\n";

# Set the current directory to the script's directory
chdir($Bin);

# Install required Perl modules
print "Checking and installing required Perl modules...\n";
my @modules = (
    'CGI',
    'CGI::Session',
    'DBI',
    'DBD::mysql',
    'Template',
    'Crypt::BCrypt',
    'Crypt::Mode::CBC',
    'Crypt::AuthEnc::GCM',
    'MIME::Base64',
    'Crypt::PRNG',
    'HTTP::Server::Simple::CGI',
    'JSON'
);

foreach my $module (@modules) {
    print "Checking for $module... ";
    eval "use $module";
    if ($@) {
        print "not found. Installing...\n";
        CPAN::install($module);
    } else {
        print "found.\n";
    }
}

# Create necessary directories
print "\nCreating necessary directories...\n";
my @dirs = ('sessions', 'db', 'logs');
foreach my $dir (@dirs) {
    if (!-d $dir) {
        mkdir $dir or die "Cannot create directory '$dir': $!";
        print "Created directory: $dir\n";
    } else {
        print "Directory '$dir' already exists.\n";
    }
}

# Set permissions
print "\nSetting directory permissions...\n";
chmod 0777, 'sessions' or warn "Cannot set permissions for 'sessions': $!";
chmod 0777, 'logs' or warn "Cannot set permissions for 'logs': $!";

# Set CGI script permissions
print "\nSetting CGI script permissions...\n";
my @cgi_files = glob("*.cgi");
foreach my $cgi (@cgi_files) {
    chmod 0755, $cgi or warn "Cannot set permissions for '$cgi': $!";
    print "Set executable permissions for: $cgi\n";
}

# Get and set database configuration
print "\nDatabase configuration (MySQL/MariaDB):\n";
print "===================================\n";
print "Please enter your database connection details:\n\n";

print "Database host [localhost]: ";
my $db_host = <STDIN>;
chomp $db_host;
$db_host = 'localhost' if $db_host eq '';

print "Database port [3306]: ";
my $db_port = <STDIN>;
chomp $db_port;
$db_port = '3306' if $db_port eq '';

print "Database name [customer_log]: ";
my $db_name = <STDIN>;
chomp $db_name;
$db_name = 'customer_log' if $db_name eq '';

print "Database username: ";
my $db_user = <STDIN>;
chomp $db_user;

print "Database password: ";
ReadMode('noecho');
my $db_pass = <STDIN>;
chomp $db_pass;
ReadMode('restore');
print "\n";

# Test database connection
print "\nTesting database connection... ";
my $dsn = "DBI:mysql:host=$db_host;port=$db_port";
my $dbh;
eval {
    $dbh = DBI->connect($dsn, $db_user, $db_pass, {RaiseError => 1, PrintError => 0});
};

if ($@) {
    print "Failed!\n";
    print "Error: $@\n";
    print "Please check your database credentials and try again.\n";
    exit 1;
} else {
    print "Success!\n";
}

# Check if database exists
my $db_exists = 0;
my $sth = $dbh->prepare("SHOW DATABASES LIKE ?");
$sth->execute($db_name);
$db_exists = 1 if $sth->fetchrow_array;

# Create database if it doesn't exist
if (!$db_exists) {
    print "\nCreating database '$db_name'... ";
    eval {
        $dbh->do("CREATE DATABASE IF NOT EXISTS $db_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
    };
    if ($@) {
        print "Failed!\n";
        print "Error: $@\n";
        exit 1;
    } else {
        print "Success!\n";
    }
}

# Connect to the specific database
$dbh->disconnect();
$dsn = "DBI:mysql:database=$db_name;host=$db_host;port=$db_port";
eval {
    $dbh = DBI->connect($dsn, $db_user, $db_pass, {RaiseError => 1, PrintError => 0});
};

# Create encryption key
print "\nGenerating encryption key for sensitive data... ";
my @chars = ('A'..'Z', 'a'..'z', '0'..'9', '_');
my $encryption_key = '';
for (1..32) {
    $encryption_key .= $chars[rand @chars];
}
print "Done.\n";

# Create or update Config.pm
print "\nUpdating configuration file... ";
my $config_content = qq{package Config;

use strict;
use warnings;
use utf8;

# Database configuration
our \$DB_HOST = '$db_host';
our \$DB_PORT = $db_port;
our \$DB_NAME = '$db_name';
our \$DB_USER = '$db_user';
our \$DB_PASS = '$db_pass';

# Encryption key for sensitive data (32 bytes for AES-256)
our \$ENCRYPTION_KEY = '$encryption_key';

# Session configuration
our \$SESSION_TIMEOUT = 3600; # Session timeout in seconds (1 hour)

1;
};

open my $config_fh, '>', 'lib/Config.pm' or die "Cannot open Config.pm for writing: $!";
print $config_fh $config_content;
close $config_fh;
print "Done.\n";

# Import database schema
print "\nImporting database schema... ";
open my $schema_fh, '<', 'sql/schema.sql' or die "Cannot open schema.sql: $!";
my $schema = do { local $/; <$schema_fh> };
close $schema_fh;

# Modify schema to skip database creation (we've already created it)
$schema =~ s/CREATE DATABASE.*?;\s*USE .*?;//s;

eval {
    my @statements = split(/;/, $schema);
    foreach my $statement (@statements) {
        $statement =~ s/^\s+|\s+$//g;
        next unless $statement;
        $dbh->do($statement);
    }
};

if ($@) {
    print "Failed!\n";
    print "Error: $@\n";
    exit 1;
} else {
    print "Success!\n";
}

# Check if default admin user exists
print "\nChecking for default admin user... ";
$sth = $dbh->prepare("SELECT id FROM users WHERE username = 'admin'");
$sth->execute();
my $admin_exists = $sth->fetchrow_array;

if (!$admin_exists) {
    print "not found. Creating admin user...\n";
    
    print "Enter admin password [admin123]: ";
    ReadMode('noecho');
    my $admin_pass = <STDIN>;
    chomp $admin_pass;
    $admin_pass = 'admin123' if $admin_pass eq '';
    ReadMode('restore');
    print "\n";
    
    # Hash the password using Crypt::BCrypt
    eval "use Crypt::BCrypt";
    my $hashed_password = Crypt::BCrypt::bcrypt($admin_pass, '$2a$10$'.Crypt::BCrypt::generate_salt(16));
    
    eval {
        $dbh->do("INSERT INTO users (username, password, full_name, is_admin, is_active) VALUES (?, ?, ?, TRUE, TRUE)",
                 undef, 'admin', $hashed_password, 'Administrator');
    };
    
    if ($@) {
        print "Failed to create admin user: $@\n";
    } else {
        print "Admin user created successfully.\n";
    }
} else {
    print "found.\n";
}

# Create basic .htaccess for Apache
print "\nCreating .htaccess for Apache... ";
my $htaccess = qq{Options +ExecCGI
AddHandler cgi-script .cgi
DirectoryIndex index.cgi
RewriteEngine On
RewriteBase /
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.cgi/$1 [QSA,L]
};

open my $htaccess_fh, '>', '.htaccess' or die "Cannot open .htaccess for writing: $!";
print $htaccess_fh $htaccess;
close $htaccess_fh;
print "Done.\n";

# Done
print "\n===========================================\n";
print "Setup completed successfully!\n";
print "===========================================\n\n";

print "You can now run the application using:\n";
print "1. For development: perl server.pl (starts on port 5000)\n";
print "2. For production: Deploy to a web server with Perl and CGI support\n\n";

print "Default login credentials:\n";
print "Username: admin\n";
print "Password: admin123 (Change this after first login!)\n\n";

$dbh->disconnect();
exit;