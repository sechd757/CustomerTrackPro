package Encryption;

use strict;
use warnings;
use Crypt::Mode::CBC;
use Crypt::AuthEnc::GCM;
use MIME::Base64;
use Crypt::PRNG qw(random_bytes);
use Config;
use utf8;

# Encrypt data using AES-CBC
sub encrypt {
    my ($plaintext) = @_;
    return '' unless defined $plaintext && length($plaintext);
    
    # Generate a random IV
    my $iv = random_bytes(16);  # 16 bytes for AES
    
    # Create a cipher object
    my $cipher = Crypt::Mode::CBC->new('AES');
    
    # Encrypt
    my $ciphertext = $cipher->encrypt($plaintext, $Config::ENCRYPTION_KEY, $iv);
    
    # Combine IV and ciphertext and encode in Base64
    return encode_base64($iv . $ciphertext, '');
}

# Decrypt data
sub decrypt {
    my ($encoded) = @_;
    return '' unless defined $encoded && length($encoded);
    
    # Decode from Base64
    my $combined = decode_base64($encoded);
    return '' if length($combined) < 16;  # Need at least IV size
    
    # Extract IV and ciphertext
    my $iv = substr($combined, 0, 16);
    my $ciphertext = substr($combined, 16);
    
    # Create a cipher object
    my $cipher = Crypt::Mode::CBC->new('AES');
    
    # Decrypt
    my $plaintext = $cipher->decrypt($ciphertext, $Config::ENCRYPTION_KEY, $iv);
    
    return $plaintext;
}

# Create a search token (simplified encryption for searchable fields)
# This is a simplistic approach - in production, consider more advanced techniques like CryptDB
sub create_search_token {
    my ($text) = @_;
    return lc($text);  # Simple lowercase for demo purposes
}

1;
