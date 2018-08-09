#!/usr/bin/env sh

while true; do
    (cat server/response_header.txt; echo -e "\n$RESPONSE_BODY" ) | nc -q 0 -lp $1
done
