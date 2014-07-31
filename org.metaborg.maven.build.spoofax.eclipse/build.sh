#!/usr/bin/env bash

set -e
set -u


# Parse input
while getopts ":q:a:e:" opt; do
  case $opt in
    q)
      INPUT_QUALIFIER=$OPTARG
      ;;
    a)
      INPUT_MAVEN_ARGS=$OPTARG
      ;;
    e)
      export MAVEN_OPTS=$OPTARG
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
fi

DIR=$(pwd)
ROOT="$DIR/../../"

STRATEGOXT_JAR="$ROOT/strategoxt/strategoxt/stratego-libraries/java-backend/java/strategoxt.jar"

GEN_LOC="$ROOT/spoofax/org.strategoxt.imp.generator/"
GEN_DIST_LOC="$GEN_LOC/dist/"

case $OSTYPE in
  linux-gnu)
    NATIVE_LOC="$ROOT/spoofax/org.strategoxt.imp.nativebundle/native/linux/"
    ;;
  darwin*)
    NATIVE_LOC="$ROOT/spoofax/org.strategoxt.imp.nativebundle/native/macosx/"
    ;;
  cygwin)
    NATIVE_LOC="$ROOT/spoofax/org.strategoxt.imp.nativebundle/native/cygwin/"
    ;;
  *)
    echo "Unsupported platform: $OSTYPE" >&2
    exit 3
    ;;
esac


mvn \
  -DforceContextQualifier=$QUALIFIER \
  -Dstrategoxt-jar=$STRATEGOXT_JAR \
  -Ddist-loc=$GEN_DIST_LOC \
  -Dnative-loc=$NATIVE_LOC \
  clean verify \
  $MAVEN_ARGS
