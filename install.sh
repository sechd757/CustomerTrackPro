#!/bin/bash
# Installation script for Customer Logging System

echo "=================================================="
echo "  Customer Logging System - Installation Script"
echo "=================================================="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root or with sudo."
  exit 1
fi

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Install system dependencies
echo "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
  # Debian/Ubuntu
  apt-get update
  apt-get install -y \
    perl \
    cpanminus \
    build-essential \
    libmysqlclient-dev \
    mariadb-client \
    libssl-dev \
    apache2 \
    libapache2-mod-perl2 \
    libcgi-pm-perl
elif command -v yum &> /dev/null; then
  # CentOS/RHEL
  yum install -y \
    perl \
    perl-App-cpanminus \
    gcc \
    mysql-devel \
    mariadb \
    openssl-devel \
    httpd \
    mod_perl
elif command -v pacman &> /dev/null; then
  # Arch Linux
  pacman -Sy --noconfirm \
    perl \
    cpanminus \
    base-devel \
    mysql \
    mariadb \
    openssl \
    apache \
    mod_perl
else
  echo "Unsupported package manager. Please install the necessary dependencies manually."
  exit 1
fi

# Install Perl dependencies
echo "Installing Perl dependencies..."
cpanm --installdeps .

# Create necessary directories
echo "Setting up directories..."
mkdir -p sessions logs db
chmod 777 sessions logs

# Set up CGI scripts permissions
echo "Setting file permissions..."
find . -name "*.cgi" -exec chmod 755 {} \;
chmod 755 server.pl setup.pl

# Set up Apache/httpd if available
if command -v a2enmod &> /dev/null; then
  echo "Configuring Apache..."
  a2enmod cgi
  a2enmod rewrite
  service apache2 restart
elif [ -d "/etc/httpd/conf.modules.d/" ]; then
  echo "Configuring httpd..."
  # For CentOS/RHEL
  echo "LoadModule cgi_module modules/mod_cgi.so" > /etc/httpd/conf.modules.d/00-cgi.conf
  service httpd restart
fi

echo
echo "=================================================="
echo "System dependencies installed successfully."
echo "Now run the Perl setup script to configure the application:"
echo
echo "perl setup.pl"
echo
echo "See DEPLOYMENT.md for more details."
echo "=================================================="