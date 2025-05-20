#!/usr/bin/perl

use strict;
use warnings;
use CGI;
use CGI::Session;
use lib './lib';
use Config;
use Database;
use Authentication;
use Template;
use Customer;
use utf8;

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
}

# Redirect to login if not authenticated
if (!$authenticated) {
    print $cgi->redirect('login.cgi');
    exit;
}

# Create database connection
my $dbh = Database::connect();
my $customer = Customer->new($dbh);

# Get dashboard data
my $total_customers = $customer->get_total_count();
my $recent_customers = $customer->get_recent(5);
my $today_count = $customer->get_count_for_date(scalar localtime);

# Set up template
my $template = Template->new({
    INCLUDE_PATH => './templates',
    ENCODING     => 'utf8',
});

# Print HTTP headers
print $cgi->header(-type => 'text/html', -charset => 'utf-8');

# Define template variables
my $vars = {
    title         => 'Customer Logging Dashboard',
    username      => $username,
    authenticated => $authenticated,
    total_customers => $total_customers,
    recent_customers => $recent_customers,
    today_count     => $today_count,
    current_month   => scalar(localtime()->mon),
    current_year    => scalar(localtime()->year + 1900),
};

# Process template
$template->process('dashboard.tt', $vars) || die $template->error();

# Clean up
$dbh->disconnect();
$session->close();

exit;
