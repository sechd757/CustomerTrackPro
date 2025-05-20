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

# Get action
my $action = $cgi->param('action') || 'list';
my $customer_id = $cgi->param('id') || '';
my $error = '';
my $success = '';

# Handle form submission
if ($cgi->param('submit')) {
    if ($action eq 'add' || $action eq 'edit') {
        my %data = (
            user => $cgi->param('user') || '',
            name => $cgi->param('name') || '',
            phone => $cgi->param('phone') || '',
            email => $cgi->param('email') || '',
            city => $cgi->param('city') || '',
            stackno => $cgi->param('stackno') || '',
            sales1 => $cgi->param('sales1') || '',
            sales2 => $cgi->param('sales2') || '',
            closer => $cgi->param('closer') || '',
            newused => $cgi->param('newused') || '',
            year => $cgi->param('year') || '',
            make => $cgi->param('make') || '',
            model => $cgi->param('model') || '',
            trade => $cgi->param('trade') || '',
            demo => $cgi->param('demo') || '',
            writeup => $cgi->param('writeup') || '',
            results => $cgi->param('results') || '',
            notes => $cgi->param('notes') || '',
        );

        # Validate required fields
        if (!$data{name} || !$data{phone}) {
            $error = 'Name and Phone are required fields';
        } else {
            # Save customer data
            if ($action eq 'add') {
                if ($customer->add(\%data)) {
                    $success = 'Customer added successfully';
                    $action = 'list'; # Redirect to list after successful add
                } else {
                    $error = 'Error adding customer: ' . $customer->error();
                }
            } elsif ($action eq 'edit') {
                if ($customer->update($customer_id, \%data)) {
                    $success = 'Customer updated successfully';
                    $action = 'list'; # Redirect to list after successful update
                } else {
                    $error = 'Error updating customer: ' . $customer->error();
                }
            }
        }
    } elsif ($action eq 'delete' && $customer_id) {
        if ($customer->delete($customer_id)) {
            $success = 'Customer deleted successfully';
            $action = 'list';
        } else {
            $error = 'Error deleting customer: ' . $customer->error();
        }
    }
}

# Get customer data for edit form
my $customer_data = {};
if ($action eq 'edit' && $customer_id) {
    $customer_data = $customer->get_by_id($customer_id);
    if (!$customer_data) {
        $error = 'Customer not found';
        $action = 'list';
    }
}

# Get customer list for list view
my $customer_list = [];
if ($action eq 'list') {
    $customer_list = $customer->get_all();
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
    title => ($action eq 'add' ? 'Add Customer' : 
              $action eq 'edit' ? 'Edit Customer' : 
              'Customer List'),
    username => $username,
    authenticated => $authenticated,
    action => $action,
    customer_id => $customer_id,
    customer => $customer_data,
    customers => $customer_list,
    error => $error,
    success => $success,
};

# Process template
my $template_file = ($action eq 'add' || $action eq 'edit') ? 'customer_form.tt' : 'customer_list.tt';
$template->process($template_file, $vars) || die $template->error();

# Clean up
$dbh->disconnect();
$session->close();

exit;
