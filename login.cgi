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
use utf8;

# Create CGI and Session objects
my $cgi = CGI->new;
my $session = CGI::Session->new("driver:File", $cgi, {Directory => './sessions'});
my $sid = $session->id();

# Check if already authenticated
if ($session->param('authenticated')) {
    print $cgi->redirect('index.cgi');
    exit;
}

# Process login
my $error = '';
if ($cgi->param('submit')) {
    my $username = $cgi->param('username');
    my $password = $cgi->param('password');
    
    # Connect to database
    my $dbh = Database::connect();
    
    # Attempt authentication
    my $auth = Authentication->new($dbh);
    my $user_id = $auth->authenticate($username, $password);
    
    if ($user_id) {
        # Set session parameters
        $session->param('authenticated', 1);
        $session->param('user_id', $user_id);
        $session->param('username', $username);
        
        # Redirect to dashboard
        print $cgi->redirect('index.cgi');
        exit;
    } else {
        $error = 'Invalid username or password';
    }
    
    $dbh->disconnect();
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
    title => 'Login - Customer Logging System',
    error => $error,
};

# Process template
$template->process('login.tt', $vars) || die $template->error();

$session->close();

exit;
