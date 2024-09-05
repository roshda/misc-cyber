#!/bin/bash

# This script checks if a password has been compromised using the Have I Been Pwned API
# instead of sending the plaintext password, it sends a portion of its SHA-1 hash to see if the password
# is in its database

# ensure a password is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 '<password>'"
    exit 1
fi

input_password="$1"

sha1_hash=$(echo -n "$input_password" | sha1sum | awk '{print $1}')

# get the first 5 characters (prefix) and the remaining characters (suffix) of the SHA-1 hash
hash_prefix="${sha1_hash:0:5}"
hash_suffix="${sha1_hash:5}"

# get the list of hashes from the HIBP API that match the prefix
response=$(curl -s "https://api.pwnedpasswords.com/range/$hash_prefix")

# check if the hash suffix is found in the response (case-insensitive)
if echo "$response" | grep -iq "$hash_suffix"; then
    echo "Password has been pwned, change it."
else
    echo "Password is safe :)"
fi
