#!/usr/bin/perl

use strict;
use warnings;
use CGI;
use CGI::Session;
use lib './lib';
use Config;
use Database;
use Authentication;
use Customer;
use Template;
use utf8;
use Time::Local;
use POSIX qw(strftime);

# Create CGI and Session objects
my $cgi = CGI->new;
my $session = CGI::Session->new("driver:File", $cgi, {Directory => './sessions'});
my $sid = $session->id();

# Check if user is authenticated
my $authenticated = 0;
my $username = "";
if ($session->param('authenticated')) {
    $authenticated = 1;
    $username = $session->param('username');
} else {
    print $cgi->redirect('login.cgi');
    exit;
}

# Create database connection
my $dbh = Database::connect();
my $customer = Customer->new($dbh);

# Get month and year, default to current
my $month = $cgi->param('month') || (localtime)[4] + 1;
my $year = $cgi->param('year') || (localtime)[5] + 1900;

# Make sure month is valid (1-12)
$month = 1 if $month < 1;
$month = 12 if $month > 12;

# Get number of days in month
my @days_in_month = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);
$days_in_month[2] = 29 if (($year % 4 == 0 && $year % 100 != 0) || $year % 400 == 0);

# Get first day of month (0 = Sunday, 6 = Saturday)
my $first_day = (localtime(timelocal(0, 0, 0, 1, $month - 1, $year - 1900)))[6];

# Get customer counts for each day of the month
my %day_counts;
for my $day (1..$days_in_month[$month]) {
    my $date_str = sprintf("%04d-%02d-%02d", $year, $month, $day);
    $day_counts{$day} = $customer->get_count_for_date($date_str);
}

# Selected day details
my $selected_day = $cgi->param('day') || '';
my $customers_for_day = [];
if ($selected_day && $selected_day >= 1 && $selected_day <= $days_in_month[$month]) {
    my $date_str = sprintf("%04d-%02d-%02d", $year, $month, $selected_day);
    $customers_for_day = $customer->get_for_date($date_str);
}

# Get previous and next month
my $prev_month = $month - 1;
my $prev_year = $year;
if ($prev_month < 1) {
    $prev_month = 12;
    $prev_year--;
}

my $next_month = $month + 1;
my $next_year = $year;
if ($next_month > 12) {
    $next_month = 1;
    $next_year++;
}

# Set up template
my $template = Template->new({
    INCLUDE_PATH => './templates',
    ENCODING     => 'utf8',
});

# Print HTTP headers
print $cgi->header(-type => 'text/html', -charset => 'utf-8');

# Month names for display
my @month_names = qw(January February March April May June July August September October November December);

# Define template variables
my $vars = {
    title => 'Customer Calendar',
    username => $username,
    authenticated => $authenticated,
    month => $month,
    year => $year,
    month_name => $month_names[$month - 1],
    first_day => $first_day,
    days_in_month => $days_in_month[$month],
    day_counts => \%day_counts,
    selected_day => $selected_day,
    customers_for_day => $customers_for_day,
    prev_month => $prev_month,
    prev_year => $prev_year,
    next_month => $next_month,
    next_year => $next_year,
};

# Process template
$template->process('calendar.tt', $vars) || die $template->error();

# Clean up
$dbh->disconnect();
$session->close();

exit;
