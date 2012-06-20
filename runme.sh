#!/usr/bin/env bash

#
# I'm sure you could do this with "watch" and the correct set of flags
# and pipe chain including cat -v, but this seemed more
# straightforward.
#

while true; do
    ./todo-sweeper.py | head 
    sleep 1
done


