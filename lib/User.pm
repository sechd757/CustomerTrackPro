package User;

use strict;
use warnings;
use Database;
use Authentication;
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

# Add a new user
sub add {
    my ($self, $data) = @_;
    
    # Validate username (must be unique)
    my $query = "SELECT id FROM users WHERE username = ?";
    my $existing = Database::fetch_record($self->{dbh}, $query, $data->{username});
    
    if ($existing) {
        $self->{error} = "Username already exists";
        return 0;
    }
    
    # Hash password
    my $hashed_password = Authentication::hash_password($data->{password});
    
    # Insert into database
    $query = "INSERT INTO users (
        username, password, full_name, email, is_admin, is_active
    ) VALUES (?, ?, ?, ?, ?, ?)";
    
    my ($sth, $error) = Database::execute($self->{dbh}, $query, 
        $data->{username},
        $hashed_password,
        $data->{full_name},
        $data->{email},
        $data->{is_admin} ? 1 : 0,
        $data->{is_active} ? 1 : 0
    );
    
    if ($error) {
        $self->{error} = "Database error: $error";
        return 0;
    }
    
    return $self->{dbh}->last_insert_id(undef, undef, 'users', 'id');
}

# Update a user
sub update {
    my ($self, $id, $data) = @_;
    
    # Check if username is being changed and if it's unique
    my $query = "SELECT id FROM users WHERE username = ? AND id != ?";
    my $existing = Database::fetch_record($self->{dbh}, $query, $data->{username}, $id);
    
    if ($existing) {
        $self->{error} = "Username already exists";
        return 0;
    }
    
    # If password is being updated, hash it
    my $password_clause = '';
    my @params = (
        $data->{username},
        $data->{full_name},
        $data->{email},
        $data->{is_admin} ? 1 : 0,
        $data->{is_active} ? 1 : 0
    );
    
    if (exists $data->{password} && $data->{password}) {
        $password_clause = ", password = ?";
        push @params, Authentication::hash_password($data->{password});
    }
    
    # Update database
    $query = "UPDATE users SET
        username = ?, full_name = ?, email = ?, 
        is_admin = ?, is_active = ?$password_clause
        WHERE id = ?";
    
    push @params, $id;
    
    my ($sth, $error) = Database::execute($self->{dbh}, $query, @params);
    
    if ($error) {
        $self->{error} = "Database error: $error";
        return 0;
    }
    
    return 1;
}

# Delete a user
sub delete {
    my ($self, $id) = @_;
    
    my $query = "DELETE FROM users WHERE id = ?";
    my ($sth, $error) = Database::execute($self->{dbh}, $query, $id);
    
    if ($error) {
        $self->{error} = "Database error: $error";
        return 0;
    }
    
    return $sth->rows > 0;
}

# Get a user by ID
sub get_by_id {
    my ($self, $id) = @_;
    
    my $query = "SELECT id, username, full_name, email, is_admin, is_active FROM users WHERE id = ?";
    my $record = Database::fetch_record($self->{dbh}, $query, $id);
    
    return $record;
}

# Get all users
sub get_all {
    my ($self) = @_;
    
    my $query = "SELECT id, username, full_name, email, is_admin, is_active FROM users ORDER BY username";
    my $records = Database::fetch_records($self->{dbh}, $query);
    
    return $records;
}

# Get error message
sub error {
    my ($self) = @_;
    return $self->{error};
}

1;
