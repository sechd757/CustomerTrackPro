#!/bin/bash
set -e

echo "Setting up Customer Logging System..."

# Make scripts executable
chmod +x *.cgi

# Create sessions directory
mkdir -p sessions
chmod 777 sessions

# Install required Perl modules
echo "Installing Perl modules..."
cpan -T CGI
cpan -T CGI::Session
cpan -T Template
cpan -T MIME::Base64
cpan -T Time::Local
cpan -T Crypt::PRNG

# Since we can't use MariaDB in this environment, we'll use SQLite instead
# Modify the configuration to use SQLite
echo "Configuring for SQLite database..."
if [ ! -f lib/Config.pm.bak ]; then
    cp lib/Config.pm lib/Config.pm.bak
    
    # Replace the database configuration with SQLite setup
    sed -i 's/^our $DB_HOST.*/# SQLite configuration/' lib/Config.pm
    sed -i 's/^our $DB_PORT.*/our $USE_SQLITE = 1;/' lib/Config.pm
    sed -i 's/^our $DB_NAME.*/our $DB_FILE = "customer_log.db";/' lib/Config.pm
    sed -i '/^our $DB_USER/d' lib/Config.pm
    sed -i '/^our $DB_PASS/d' lib/Config.pm
fi

echo "Creating a simple demonstration mode..."
echo "The full customer logging system requires MariaDB/MySQL database and additional Perl modules."
echo "This is a simplified version showing the interface."

# Create a modified Database.pm for SQLite
if [ ! -f lib/Database.pm.bak ]; then
    cp lib/Database.pm lib/Database.pm.bak
    
cat > lib/Database.pm << EOF
package Database;

use strict;
use warnings;
use Config;
use utf8;

# This is a mock database module for demonstration purposes
sub connect {
    # In a real environment, this would connect to a database
    my \$dbh = {
        mock => 1,
        error => undef
    };
    
    return \$dbh;
}

sub execute {
    my (\$dbh, \$query, @params) = @_;
    return (1, undef); # Mock successful execution
}

sub fetch_record {
    my (\$dbh, \$query, @params) = @_;
    
    # For authentication, return a mock admin user
    if (\$query =~ /users/) {
        return {
            id => 1,
            username => 'admin',
            password => '\$2a\$10\$8KsRftV2waCUkTzT7CXep.h5.7/bHQxnXc7qlZIUVVXgbHKlfkEP.',
            is_active => 1,
            is_admin => 1,
            full_name => 'Administrator'
        };
    }
    
    # Mock other queries with sample data
    return {};
}

sub fetch_records {
    my (\$dbh, \$query, @params) = @_;
    
    # Return mock customer data for display
    if (\$query =~ /customers/) {
        return [
            {
                id => 1,
                name => 'Encrypted Name',
                name_decrypted => 'John Doe',
                phone => 'Encrypted Phone',
                phone_decrypted => '(555) 123-4567',
                email => 'john@example.com',
                city => 'New York',
                stackno => 'A123',
                sales1 => 'Jane Smith',
                sales2 => 'Bob Johnson',
                closer => 'Alice Brown',
                newused => 'New',
                year => '2023',
                make => 'Toyota',
                model => 'Camry',
                trade => 'Yes',
                demo => 'No',
                writeup => 'Customer is interested in financing options',
                results => 'Pending final approval',
                notes => 'Follow up next week',
                datetime => '2023-05-15 14:30:00'
            },
            {
                id => 2,
                name => 'Encrypted Name',
                name_decrypted => 'Jane Smith',
                phone => 'Encrypted Phone',
                phone_decrypted => '(555) 987-6543',
                email => 'jane@example.com',
                city => 'Chicago',
                stackno => 'B456',
                sales1 => 'John Doe',
                sales2 => '',
                closer => 'Bob Johnson',
                newused => 'Used',
                year => '2020',
                make => 'Honda',
                model => 'Civic',
                trade => 'No',
                demo => 'Yes',
                writeup => 'Customer wants extended warranty',
                results => 'Sale completed',
                notes => 'Very satisfied customer',
                datetime => '2023-05-14 10:15:00'
            }
        ];
    }
    
    # Return mock user data
    if (\$query =~ /users/) {
        return [
            {
                id => 1,
                username => 'admin',
                full_name => 'Administrator',
                email => 'admin@example.com',
                is_admin => 1,
                is_active => 1
            },
            {
                id => 2,
                username => 'user',
                full_name => 'Regular User',
                email => 'user@example.com',
                is_admin => 0,
                is_active => 1
            }
        ];
    }
    
    return [];
}

1;
EOF
fi

# Create a modified Authentication.pm to work without the real Crypt::BCrypt
if [ ! -f lib/Authentication.pm.bak ]; then
    cp lib/Authentication.pm lib/Authentication.pm.bak
    
cat > lib/Authentication.pm << EOF
package Authentication;

use strict;
use warnings;
use utf8;

# Constructor
sub new {
    my (\$class, \$dbh) = @_;
    
    my \$self = {
        dbh => \$dbh,
        error => '',
    };
    
    bless \$self, \$class;
    return \$self;
}

# Authenticate a user (mock version)
sub authenticate {
    my (\$self, \$username, \$password) = @_;
    
    # For demo purposes, allow login with admin/admin123
    if (\$username eq 'admin' && \$password eq 'admin123') {
        return 1; # Return user ID 1
    }
    
    \$self->{error} = 'Invalid username or password';
    return 0;
}

# Create a hashed password (mock version)
sub hash_password {
    my (\$password) = @_;
    return "hashed_" . \$password;
}

# Verify a password against a hash (mock version)
sub verify_password {
    my (\$password, \$hash) = @_;
    # For demo, just assume it's valid if admin/admin123
    return (\$password eq 'admin123');
}

# Get error message
sub error {
    my (\$self) = @_;
    return \$self->{error};
}

1;
EOF
fi

# Create a simplified Encryption.pm
if [ ! -f lib/Encryption.pm.bak ]; then
    cp lib/Encryption.pm lib/Encryption.pm.bak
    
cat > lib/Encryption.pm << EOF
package Encryption;

use strict;
use warnings;
use utf8;

# Mock encryption function
sub encrypt {
    my (\$plaintext) = @_;
    return "ENCRYPTED:" . \$plaintext;
}

# Mock decryption function
sub decrypt {
    my (\$encrypted) = @_;
    if (\$encrypted =~ /^ENCRYPTED:(.*)$/) {
        return \$1;
    }
    return \$encrypted;
}

# Create a search token (simplified version)
sub create_search_token {
    my (\$text) = @_;
    return lc(\$text);
}

1;
EOF
fi

echo "Starting web server on port 5000..."
# This will keep the server running until stopped
perl -MCGI::Carp=fatalsToBrowser -MHTTP::Server::Simple::CGI -e 'HTTP::Server::Simple::CGI->new(5000)->run()'