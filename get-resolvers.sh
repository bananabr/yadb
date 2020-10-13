#!/bin/bash
COUNTRY_CODE=${1:-"US"}

curl https://public-dns.info/nameservers.csv | cut -d , -f 1,5,10,11 | grep $COUNTRY_CODE | grep ',0\.9.,' | sort --field-separator=',' -k 3 -r | cut -d , -f 1 | grep -v : > resolvers.txt
