#!/usr/bin/perl

use strict;
use warnings;
use CGI;
use CGI::Session;

# Create CGI and Session objects
my $cgi = CGI->new;
my $session = CGI::Session->new("driver:File", $cgi, {Directory => './sessions'});

# Clear the session
$session->delete();
$session->flush();

# Redirect to login page
print $cgi->redirect('login.cgi');

exit;
