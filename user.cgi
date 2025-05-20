#!/usr/bin/perl

use strict;
use warnings;
use CGI;
use CGI::Session;
use lib './lib';
use Config;
use Database;
use Authentication;
use User;
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
my $user = User->new($dbh);

# Get action
my $action = $cgi->param('action') || 'list';
my $user_id = $cgi->param('id') || '';
my $error = '';
my $success = '';

# Handle form submission
if ($cgi->param('submit')) {
    if ($action eq 'add' || $action eq 'edit') {
        my %data = (
            username => $cgi->param('username') || '',
            password => $cgi->param('password') || '',
            full_name => $cgi->param('full_name') || '',
            email => $cgi->param('email') || '',
            is_admin => $cgi->param('is_admin') ? 1 : 0,
            is_active => $cgi->param('is_active') ? 1 : 0,
        );

        # Validate required fields
        if (!$data{username} || ($action eq 'add' && !$data{password})) {
            $error = 'Username and Password are required fields';
        } else {
            # Save user data
            if ($action eq 'add') {
                if ($user->add(\%data)) {
                    $success = 'User added successfully';
                    $action = 'list'; # Redirect to list after successful add
                } else {
                    $error = 'Error adding user: ' . $user->error();
                }
            } elsif ($action eq 'edit') {
                # Don't update password if it's empty (unchanged)
                delete $data{password} if !$data{password};
                
                if ($user->update($user_id, \%data)) {
                    $success = 'User updated successfully';
                    $action = 'list'; # Redirect to list after successful update
                } else {
                    $error = 'Error updating user: ' . $user->error();
                }
            }
        }
    } elsif ($action eq 'delete' && $user_id) {
        # Don't allow deletion of own account
        if ($user_id == $session->param('user_id')) {
            $error = 'You cannot delete your own account';
        } else {
            if ($user->delete($user_id)) {
                $success = 'User deleted successfully';
                $action = 'list';
            } else {
                $error = 'Error deleting user: ' . $user->error();
            }
        }
    }
}

# Get user data for edit form
my $user_data = {};
if ($action eq 'edit' && $user_id) {
    $user_data = $user->get_by_id($user_id);
    if (!$user_data) {
        $error = 'User not found';
        $action = 'list';
    }
}

# Get user list for list view
my $user_list = [];
if ($action eq 'list') {
    $user_list = $user->get_all();
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
    title => ($action eq 'add' ? 'Add User' : 
              $action eq 'edit' ? 'Edit User' : 
              'User Management'),
    username => $username,
    authenticated => $authenticated,
    action => $action,
    user_id => $user_id,
    user => $user_data,
    users => $user_list,
    error => $error,
    success => $success,
    current_user_id => $session->param('user_id'),
};

# Process template
my $template_file = ($action eq 'add' || $action eq 'edit') ? 'user_form.tt' : 'user_list.tt';
$template->process($template_file, $vars) || die $template->error();

# Clean up
$dbh->disconnect();
$session->close();

exit;
