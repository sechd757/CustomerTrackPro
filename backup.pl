#!/usr/bin/perl

use strict;
use warnings;
use lib './lib';
use Config;
use POSIX qw(strftime);
use File::Path qw(make_path);

my $backup_dir = "backups";
make_path($backup_dir) unless -d $backup_dir;

my $timestamp = strftime("%Y%m%d-%H%M%S", localtime);
my $backup_file = "$backup_dir/customer_log-$timestamp.sql";

print "\n";
print "=========================================\n";
print "Customer Logging System - Database Backup\n";
print "=========================================\n\n";

print "Backing up database '$Config::DB_NAME' to $backup_file...\n";

my $command = "mysqldump -h $Config::DB_HOST -P $Config::DB_PORT -u $Config::DB_USER";
$command .= " -p'$Config::DB_PASS'" if $Config::DB_PASS;
$command .= " --single-transaction --routines --triggers";
$command .= " --add-drop-table --skip-comments $Config::DB_NAME > $backup_file";

system($command);

if ($? == 0) {
    # Backup successful
    print "Backup completed successfully!\n";
    print "Backup file: $backup_file\n";
    
    # Compress the backup file
    print "Compressing backup file...\n";
    system("gzip $backup_file");
    
    if ($? == 0) {
        print "Compression completed: $backup_file.gz\n";
    } else {
        print "Warning: Failed to compress backup file, but the SQL backup was completed.\n";
    }
} else {
    print "Error: Backup failed with exit code " . ($? >> 8) . "\n";
    print "Please make sure you have mysqldump installed and your database credentials are correct.\n";
    exit 1;
}

print "\nDone.\n";
exit 0;