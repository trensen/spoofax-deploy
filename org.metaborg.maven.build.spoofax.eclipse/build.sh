#!/usr/bin/env bash

set -e
set -u


# Parse input
while getopts ":dq:a:e:" opt; do
  case $opt in
    d)
      INPUT_MAVEN_DEPLOY="deploy"
      ;;
    q)
      INPUT_QUALIFIER=$OPTARG
      ;;
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
QUALIFIER=${INPUT_QUALIFIER:-$(date +%Y%m%d%H%M)}

MAVEN_ARGS=${INPUT_MAVEN_ARGS:-""}
if [ -z ${INPUT_MAVEN_ENV+x} ]; then
  export MAVEN_OPTS="-Xmx512m -Xms512m -Xss16m"
else
  export MAVEN_OPTS="$INPUT_MAVEN_ENV"
fi
MAVEN_DEPLOY=${INPUT_MAVEN_DEPLOY:-""}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT="$DIR/../.."

mvn \
  -f "$DIR/pom.xml" \
  -DforceContextQualifier=$QUALIFIER \
  clean install \
  $MAVEN_ARGS
  
