#!/usr/bin/env bash

set -eu


# Parse input
while getopts ":da:" opt; do
  case $opt in
    d)
      INPUT_MAVEN_PHASE="deploy"
      ;;
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
MAVEN_PHASE=${INPUT_MAVEN_PHASE:-"install"}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


# Run Maven build
mvn \
  -f "$DIR/pom.xml" \
  clean \
  $MAVEN_PHASE \
  $MAVEN_ARGS
