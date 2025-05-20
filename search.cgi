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

# Get search parameters
my $search_term = $cgi->param('search_term') || '';
my $search_field = $cgi->param('search_field') || 'all';
my $results = [];

# Perform search if search term provided
if ($search_term) {
    $results = $customer->search($search_term, $search_field);
}

# Set up template
my $template = Template->new({
    INCLUDE_PATH => './templates',
    ENCODING     => 'utf8',
});

# Print HTTP headers
print $cgi->header(-type => 'text/html', -charset => 'utf-8');

# Define template variables
my $vars = {
    title => 'Search Customers',
    username => $username,
    authenticated => $authenticated,
    search_term => $search_term,
    search_field => $search_field,
    results => $results,
    searched => $search_term ? 1 : 0,
};

# Process template
$template->process('search.tt', $vars) || die $template->error();

# Clean up
$dbh->disconnect();
$session->close();

exit;
