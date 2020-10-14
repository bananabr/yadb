#!/bin/bash
COUNTRY_CODE=${1:-".*"}
RELIABILITY=${2:-"9"}
curl https://public-dns.info/nameservers.csv 2> /dev/null | cut -d , -f 1,5,10,11 | grep -e "$COUNTRY_CODE" | grep ",0\.$RELIABILITY.," | sort --field-separator=',' -k 3 -r | cut -d , -f 1 | grep -v :
