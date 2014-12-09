#!/usr/bin/env bash

set -eu


# Parse input
while getopts ":a:" opt; do
  case $opt in
    a)
      INPUT_MAVEN_ARGS=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 2
      ;;
  esac
done


# Set build vars
MAVEN_ARGS=${INPUT_MAVEN_ARGS:-""}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


# Run Maven build
mvn \
  -f "$DIR/pom.xml" \
  clean verify \
  $MAVEN_ARGS
