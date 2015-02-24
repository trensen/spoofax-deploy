#!/usr/bin/env bash

set -eu

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pip3 install -q -r "$DIR/requirements.txt"
python3 "$DIR/src/main.py" $*
