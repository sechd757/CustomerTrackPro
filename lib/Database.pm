package Database;

use strict;
use warnings;
use DBI;
use Config;
use utf8;

# Connect to the database
sub connect {
    my $dsn = "DBI:mysql:database=$Config::DB_NAME;host=$Config::DB_HOST;port=$Config::DB_PORT";
    my $dbh = DBI->connect($dsn, $Config::DB_USER, $Config::DB_PASS, {
        RaiseError => 1,
        AutoCommit => 1,
        mysql_enable_utf8 => 1,
    }) or die "Cannot connect to database: $DBI::errstr";
    
    # Set UTF-8 connection
    $dbh->do("SET NAMES 'utf8'");
    
    return $dbh;
}

# Execute a query with parameters
sub execute {
    my ($dbh, $query, @params) = @_;
    
    my $sth = $dbh->prepare($query);
    if (!$sth) {
        return (undef, $dbh->errstr);
    }
    
    my $result = $sth->execute(@params);
    if (!defined $result) {
        return (undef, $sth->errstr);
    }
    
    return ($sth, undef);
}

# Get a single record
sub fetch_record {
    my ($dbh, $query, @params) = @_;
    
    my ($sth, $error) = execute($dbh, $query, @params);
    return undef if $error;
    
    my $record = $sth->fetchrow_hashref();
    $sth->finish();
    
    return $record;
}

# Get multiple records
sub fetch_records {
    my ($dbh, $query, @params) = @_;
    
    my ($sth, $error) = execute($dbh, $query, @params);
    return [] if $error;
    
    my @records;
    while (my $record = $sth->fetchrow_hashref()) {
        push @records, $record;
    }
    $sth->finish();
    
    return \@records;
}

1;
