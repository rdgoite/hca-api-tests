#!/usr/bin/env sh

while true; do
    cat server/default_response.txt | nc -q 0 -lp $1
done
