package Customer;

use strict;
use warnings;
use Database;
use Encryption;
use utf8;
use POSIX qw(strftime);

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

# Add a new customer
sub add {
    my ($self, $data) = @_;
    
    # Encrypt sensitive fields
    my $encrypted_name = Encryption::encrypt($data->{name});
    my $encrypted_phone = Encryption::encrypt($data->{phone});
    
    # Create search tokens for encrypted fields
    my $name_token = Encryption::create_search_token($data->{name});
    my $phone_token = Encryption::create_search_token($data->{phone});
    
    # Set current timestamp if not provided
    $data->{datetime} ||= strftime('%Y-%m-%d %H:%M:%S', localtime);
    
    # Insert into database
    my $query = "INSERT INTO customers (
        user, name, name_token, phone, phone_token, email, city, 
        stackno, sales1, sales2, closer, newused, year, make, model, 
        trade, demo, writeup, results, notes, datetime
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
    
    my ($sth, $error) = Database::execute($self->{dbh}, $query, 
        $data->{user}, 
        $encrypted_name, 
        $name_token,
        $encrypted_phone, 
        $phone_token,
        $data->{email},
        $data->{city},
        $data->{stackno},
        $data->{sales1},
        $data->{sales2},
        $data->{closer},
        $data->{newused},
        $data->{year},
        $data->{make},
        $data->{model},
        $data->{trade},
        $data->{demo},
        $data->{writeup},
        $data->{results},
        $data->{notes},
        $data->{datetime}
    );
    
    if ($error) {
        $self->{error} = "Database error: $error";
        return 0;
    }
    
    return $self->{dbh}->last_insert_id(undef, undef, 'customers', 'id');
}

# Update a customer
sub update {
    my ($self, $id, $data) = @_;
    
    # Get the current record to see what needs updating
    my $current = $self->get_by_id($id);
    if (!$current) {
        $self->{error} = "Customer not found";
        return 0;
    }
    
    # Encrypt sensitive fields if they have changed
    my $encrypted_name = $data->{name} ne $current->{name_decrypted} ? 
        Encryption::encrypt($data->{name}) : $current->{name};
    
    my $encrypted_phone = $data->{phone} ne $current->{phone_decrypted} ?
        Encryption::encrypt($data->{phone}) : $current->{phone};
    
    # Create search tokens for encrypted fields if changed
    my $name_token = $data->{name} ne $current->{name_decrypted} ?
        Encryption::create_search_token($data->{name}) : $current->{name_token};
    
    my $phone_token = $data->{phone} ne $current->{phone_decrypted} ?
        Encryption::create_search_token($data->{phone}) : $current->{phone_token};
    
    # Update database
    my $query = "UPDATE customers SET
        user = ?, name = ?, name_token = ?, phone = ?, phone_token = ?, 
        email = ?, city = ?, stackno = ?, sales1 = ?, sales2 = ?, 
        closer = ?, newused = ?, year = ?, make = ?, model = ?, 
        trade = ?, demo = ?, writeup = ?, results = ?, notes = ?
        WHERE id = ?";
    
    my ($sth, $error) = Database::execute($self->{dbh}, $query, 
        $data->{user}, 
        $encrypted_name, 
        $name_token,
        $encrypted_phone, 
        $phone_token,
        $data->{email},
        $data->{city},
        $data->{stackno},
        $data->{sales1},
        $data->{sales2},
        $data->{closer},
        $data->{newused},
        $data->{year},
        $data->{make},
        $data->{model},
        $data->{trade},
        $data->{demo},
        $data->{writeup},
        $data->{results},
        $data->{notes},
        $id
    );
    
    if ($error) {
        $self->{error} = "Database error: $error";
        return 0;
    }
    
    return 1;
}

# Delete a customer
sub delete {
    my ($self, $id) = @_;
    
    my $query = "DELETE FROM customers WHERE id = ?";
    my ($sth, $error) = Database::execute($self->{dbh}, $query, $id);
    
    if ($error) {
        $self->{error} = "Database error: $error";
        return 0;
    }
    
    return $sth->rows > 0;
}

# Get a customer by ID
sub get_by_id {
    my ($self, $id) = @_;
    
    my $query = "SELECT * FROM customers WHERE id = ?";
    my $record = Database::fetch_record($self->{dbh}, $query, $id);
    
    if ($record) {
        # Decrypt sensitive fields
        $record->{name_decrypted} = Encryption::decrypt($record->{name});
        $record->{phone_decrypted} = Encryption::decrypt($record->{phone});
    }
    
    return $record;
}

# Get all customers
sub get_all {
    my ($self) = @_;
    
    my $query = "SELECT * FROM customers ORDER BY datetime DESC";
    my $records = Database::fetch_records($self->{dbh}, $query);
    
    # Decrypt sensitive fields
    foreach my $record (@$records) {
        $record->{name_decrypted} = Encryption::decrypt($record->{name});
        $record->{phone_decrypted} = Encryption::decrypt($record->{phone});
    }
    
    return $records;
}

# Get recent customers
sub get_recent {
    my ($self, $limit) = @_;
    $limit ||= 10;
    
    my $query = "SELECT * FROM customers ORDER BY datetime DESC LIMIT ?";
    my $records = Database::fetch_records($self->{dbh}, $query, $limit);
    
    # Decrypt sensitive fields
    foreach my $record (@$records) {
        $record->{name_decrypted} = Encryption::decrypt($record->{name});
        $record->{phone_decrypted} = Encryption::decrypt($record->{phone});
    }
    
    return $records;
}

# Search customers
sub search {
    my ($self, $term, $field) = @_;
    
    my $query;
    my @params;
    
    # Create search token
    my $search_token = Encryption::create_search_token($term);
    
    if ($field eq 'name') {
        $query = "SELECT * FROM customers WHERE name_token LIKE ? ORDER BY datetime DESC";
        @params = ("%$search_token%");
    }
    elsif ($field eq 'phone') {
        $query = "SELECT * FROM customers WHERE phone_token LIKE ? ORDER BY datetime DESC";
        @params = ("%$search_token%");
    }
    elsif ($field eq 'email') {
        $query = "SELECT * FROM customers WHERE email LIKE ? ORDER BY datetime DESC";
        @params = ("%$term%");
    }
    elsif ($field eq 'city') {
        $query = "SELECT * FROM customers WHERE city LIKE ? ORDER BY datetime DESC";
        @params = ("%$term%");
    }
    else {
        # Search across multiple fields
        $query = "SELECT * FROM customers WHERE 
            name_token LIKE ? OR 
            phone_token LIKE ? OR 
            email LIKE ? OR 
            city LIKE ? OR
            stackno LIKE ? OR
            sales1 LIKE ? OR
            sales2 LIKE ? OR
            closer LIKE ? OR
            make LIKE ? OR
            model LIKE ?
            ORDER BY datetime DESC";
        @params = (("%$search_token%") x 2, ("%$term%") x 8);
    }
    
    my $records = Database::fetch_records($self->{dbh}, $query, @params);
    
    # Decrypt sensitive fields
    foreach my $record (@$records) {
        $record->{name_decrypted} = Encryption::decrypt($record->{name});
        $record->{phone_decrypted} = Encryption::decrypt($record->{phone});
    }
    
    return $records;
}

# Get customers for a specific date
sub get_for_date {
    my ($self, $date) = @_;
    
    my $query = "SELECT * FROM customers WHERE DATE(datetime) = ? ORDER BY datetime DESC";
    my $records = Database::fetch_records($self->{dbh}, $query, $date);
    
    # Decrypt sensitive fields
    foreach my $record (@$records) {
        $record->{name_decrypted} = Encryption::decrypt($record->{name});
        $record->{phone_decrypted} = Encryption::decrypt($record->{phone});
    }
    
    return $records;
}

# Get total count of customers
sub get_total_count {
    my ($self) = @_;
    
    my $query = "SELECT COUNT(*) AS count FROM customers";
    my $record = Database::fetch_record($self->{dbh}, $query);
    
    return $record ? $record->{count} : 0;
}

# Get count of customers for a specific date
sub get_count_for_date {
    my ($self, $date) = @_;
    
    my $query = "SELECT COUNT(*) AS count FROM customers WHERE DATE(datetime) = ?";
    my $record = Database::fetch_record($self->{dbh}, $query, $date);
    
    return $record ? $record->{count} : 0;
}

# Get error message
sub error {
    my ($self) = @_;
    return $self->{error};
}

1;
