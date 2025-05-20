package Authentication;

use strict;
use warnings;
use Crypt::BCrypt;
use utf8;

# Constructor
sub new {
    my ($class, $dbh) = @_;
    
    my $self = {
        dbh => $dbh,
        error => '',
    };
    
    bless $self, $class;
    return $self;
}

# Authenticate a user
sub authenticate {
    my ($self, $username, $password) = @_;
    
    # Input validation
    if (!$username || !$password) {
        $self->{error} = 'Username and password are required';
        return 0;
    }
    
    # Get user from database
    my $query = "SELECT id, username, password, is_active FROM users WHERE username = ?";
    my $user = Database::fetch_record($self->{dbh}, $query, $username);
    
    # Check if user exists
    if (!$user) {
        $self->{error} = 'Invalid username or password';
        return 0;
    }
    
    # Check if user is active
    if (!$user->{is_active}) {
        $self->{error} = 'This account has been deactivated';
        return 0;
    }
    
    # Verify password
    if (!verify_password($password, $user->{password})) {
        $self->{error} = 'Invalid username or password';
        return 0;
    }
    
    # Return user ID on successful authentication
    return $user->{id};
}

# Create a hashed password
sub hash_password {
    my ($password) = @_;
    return bcrypt($password, '$2a$10$'.generate_salt(16));
}

# Verify a password against a hash
sub verify_password {
    my ($password, $hash) = @_;
    return bcrypt_check($password, $hash);
}

# Get error message
sub error {
    my ($self) = @_;
    return $self->{error};
}

1;
