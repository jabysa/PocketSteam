#!/bin/sh
cd "$(dirname "$0")" || exit 1
python3 pocketsteam.py
result=$?
if [ "$result" -ne 0 ]; then
  printf '\nPress Enter to close... '
  read answer
fi
exit "$result"
