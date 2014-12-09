#!/bin/bash

#
# cleanup.sh
#
find . -type f -name '*.py[co]' -delete
find . -type f -name '*~' -delete
find . -type d -name '__pycache__' -delete
