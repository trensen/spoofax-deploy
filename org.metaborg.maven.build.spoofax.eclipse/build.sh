#!/usr/bin/env bash

set -eu


# Parse input
while getopts ":dq:a:" opt; do
  case $opt in
    d)
      INPUT_MAVEN_PHASE="deploy"
      ;;
    q)
      INPUT_QUALIFIER=$OPTARG
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
QUALIFIER=${INPUT_QUALIFIER:-$(date +%Y%m%d%H%M)}

MAVEN_ARGS=${INPUT_MAVEN_ARGS:-""}
MAVEN_PHASE=${INPUT_MAVEN_PHASE:-"install"}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


# Run Maven build
mvn \
  -f "$DIR/pom.xml" \
  -DforceContextQualifier=$QUALIFIER \
  clean \
  $MAVEN_PHASE \
  $MAVEN_ARGS
