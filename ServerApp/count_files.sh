#!/bin/sh

# To be used on server side under /etc/TIX/records forlder just for knowing how many files each directory has

find -maxdepth 1 -type d | while read -r dir; do printf "%s:\t" "$dir"; find "$dir" -type f | wc -l; done