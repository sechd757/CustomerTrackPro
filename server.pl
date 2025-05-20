#!/usr/bin/perl

use strict;
use warnings;
use CGI;
use CGI::Session;
use HTTP::Server::Simple::CGI;
use base qw(HTTP::Server::Simple::CGI);

# Create sessions directory
mkdir "sessions" unless -d "sessions";
chmod 0777, "sessions";

# Make sure CGI scripts are executable
foreach my $script (glob("*.cgi")) {
    chmod 0755, $script;
}

# This is a simple router to handle CGI requests
sub handle_request {
    my ($self, $cgi) = @_;
    
    # Get the requested path
    my $path = $ENV{PATH_INFO} || "/";
    
    # Default to index.cgi if no path specified
    if ($path eq '/' || $path eq '') {
        $path = '/index.cgi';
    }
    
    # Strip leading slash
    $path =~ s/^\///;
    
    # Check if requested file exists
    if (-f $path) {
        # Execute the CGI script
        print "Content-Type: text/html\r\n\r\n";
        
        # Check if we need to redirect to login page
        if ($path ne 'login.cgi' && !check_auth()) {
            print redirect_to_login();
            return;
        }
        
        # Capture and print the output of the CGI script
        if (open(my $fh, '-|', "perl $path")) {
            while (my $line = <$fh>) {
                print $line;
            }
            close($fh);
        } else {
            print "Error executing CGI script: $!";
        }
    } else {
        # 404 Not Found
        print "HTTP/1.0 404 Not Found\r\n\r\n";
        print "<html><body><h1>404 Not Found</h1>";
        print "<p>The requested URL $path was not found on this server.</p>";
        print "</body></html>";
    }
}

# Check if user is authenticated
sub check_auth {
    # For demo purposes, always return true so pages can be viewed
    return 1;
}

# Redirect to login page
sub redirect_to_login {
    return qq{
        <html>
        <head>
            <meta http-equiv="refresh" content="0;url=/login.cgi">
            <title>Redirecting...</title>
        </head>
        <body>
            <p>Redirecting to login page...</p>
            <script>window.location.href = '/login.cgi';</script>
        </body>
        </html>
    };
}

# Create and run the server
my $server = __PACKAGE__->new(5000);
print "Customer Logging System started on port 5000...\n";
$server->run();