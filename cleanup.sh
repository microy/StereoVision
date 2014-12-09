#!/bin/bash

#
# cleanup.sh
#
find . -type f -name '*.py[co]' -exec rm -v {} \;
find . -type f -name '*~' -exec rm -v {} \;
find . -type d -name '__pycache__' -exec rmdir -v {} \;
