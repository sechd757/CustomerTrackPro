#!/usr/bin/perl

use strict;
use warnings;
use lib './lib';
use Config;
use DBI;
use File::Basename;

# Initialize a database connection
my $dsn = "DBI:mysql:database=$Config::DB_NAME;host=$Config::DB_HOST;port=$Config::DB_PORT";
my $dbh = DBI->connect($dsn, $Config::DB_USER, $Config::DB_PASS, {
    RaiseError => 1,
    AutoCommit => 1,
    mysql_enable_utf8 => 1,
}) or die "Cannot connect to database: $DBI::errstr";

print "\n";
print "======================================\n";
print "Customer Logging System - DB Migration\n";
print "======================================\n\n";

# Create the schema version table if it doesn't exist
$dbh->do(
    "CREATE TABLE IF NOT EXISTS schema_version (
        version INT NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        description VARCHAR(255)
    )"
) or die "Failed to create schema_version table: " . $dbh->errstr;

# Get the current schema version
my $current_version = 0;
my $sth = $dbh->prepare("SELECT MAX(version) AS version FROM schema_version");
$sth->execute();
if (my $row = $sth->fetchrow_hashref()) {
    $current_version = $row->{version} || 0;
}
$sth->finish();

print "Current database schema version: $current_version\n\n";

# Get available migration files
my @migration_files = glob("sql/migrations/*.sql");
my %migrations;

foreach my $file (@migration_files) {
    my $filename = basename($file);
    if ($filename =~ /^(\d+)_/) {
        my $version = int($1);
        $migrations{$version} = {
            file => $file,
            name => $filename
        };
    }
}

# Sort versions
my @versions = sort {$a <=> $b} keys %migrations;
my $latest_version = $versions[-1] || 0;

if ($current_version >= $latest_version) {
    print "Database is already at the latest version ($current_version).\n";
    exit 0;
}

print "Available migrations:\n";
foreach my $version (@versions) {
    next if $version <= $current_version;
    print "  $migrations{$version}->{name}\n";
}
print "\n";

# Ask confirmation before proceeding
print "Do you want to migrate from version $current_version to $latest_version? [y/N] ";
my $confirm = <STDIN>;
chomp $confirm;
if (lc($confirm) ne 'y') {
    print "Migration aborted.\n";
    exit 0;
}

# Apply migrations in order
print "\nApplying migrations...\n";
foreach my $version (@versions) {
    next if $version <= $current_version;
    
    my $file = $migrations{$version}->{file};
    print "Applying migration: $migrations{$version}->{name}... ";
    
    # Read SQL file
    open my $fh, '<', $file or die "Cannot open $file: $!";
    my $sql = do { local $/; <$fh> };
    close $fh;
    
    # Extract description from SQL file (first line comment)
    my $description = '';
    if ($sql =~ /^--\s*(.*?)$/m) {
        $description = $1;
    }
    
    # Apply transaction if possible
    eval {
        $dbh->begin_work();
        
        # Split SQL into individual statements
        my @statements = split(/;/, $sql);
        foreach my $statement (@statements) {
            $statement =~ s/^\s+|\s+$//g;
            next unless $statement;
            
            $dbh->do($statement);
        }
        
        # Record the migration
        $dbh->do(
            "INSERT INTO schema_version (version, description) VALUES (?, ?)",
            undef, $version, $description
        );
        
        $dbh->commit();
    };
    
    if ($@) {
        $dbh->rollback();
        print "FAILED!\n";
        print "Error: $@\n";
        exit 1;
    } else {
        print "OK\n";
    }
}

print "\nMigration completed successfully.\n";
print "Database schema version is now: $latest_version\n";

$dbh->disconnect();