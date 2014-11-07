#!/usr/bin/env bash

set -e
set -u

# Parse input
while getopts ":a:e:" opt; do
  case $opt in
    a)
      INPUT_MAVEN_ARGS=$OPTARG
      ;;
    e)
      INPUT_MAVEN_ENV=$OPTARG
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
if [ -z ${INPUT_MAVEN_ENV+x} ]; then
  export MAVEN_OPTS="-Xmx512m -Xms512m -Xss16m"
else
  export MAVEN_OPTS="$INPUT_MAVEN_ENV"
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


# Build shaded JAR
mvn \
  -f "$DIR/pom.xml" \
  clean verify \
  $MAVEN_ARGS
