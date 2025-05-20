package Config;

use strict;
use warnings;
use utf8;

# Database configuration
our $DB_HOST = 'localhost';
our $DB_PORT = 3306;
our $DB_NAME = 'customer_log';
our $DB_USER = 'customer_log_user';
our $DB_PASS = 'change_this_password';

# Encryption key for sensitive data (32 bytes for AES-256)
our $ENCRYPTION_KEY = 'this_is_a_32_byte_secret_key_change_me';

# Session configuration
our $SESSION_TIMEOUT = 3600; # Session timeout in seconds (1 hour)

1;
