#!/usr/bin/env sh

while true; do
    (echo -e $RESPONSE_HEADER; echo -e "\n$RESPONSE_BODY" ) | nc -q 0 -lp $1
done
