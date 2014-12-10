#!/bin/bash

#
# cleanup.sh
#
find . -type f -name '*.py[co]' -print -delete
find . -type f -name '*~' -print -delete
find . -type d -name '__pycache__' -print -delete
