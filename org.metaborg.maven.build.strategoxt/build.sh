#!/usr/bin/env bash

set -eu


# Parse input
while getopts ":uda:" opt; do
  case $opt in
    u)
      UPDATE_DISTRIB="true"
      ;;
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

STRATEGOXT_DISTRIB_TAR="$DIR/strategoxt-distrib.tar"
STRATEGOXT_DISTRIB="$DIR/strategoxt-distrib/"
STRATEGOXT_JAR="$STRATEGOXT_DISTRIB/share/strategoxt/strategoxt/strategoxt.jar"
STRATEGOXT_MIN="$DIR/strategoxt-min"
STRATEGOXT_MIN_JAR="$DIR/strategoxt-min.jar"


# Update strategoxt distribution if it does not exist, or if requested
if [ -n "${UPDATE_DISTRIB+1}" ] || [ ! -f $STRATEGOXT_JAR ]; then
	$("$DIR/update.sh" $STRATEGOXT_DISTRIB_TAR $STRATEGOXT_DISTRIB)
fi


# Create minified strategoxt JAR
$("$DIR/minify.sh" $STRATEGOXT_JAR $STRATEGOXT_MIN $STRATEGOXT_MIN_JAR)


# Run Maven build
mvn \
  -f "$DIR/pom.xml" \
  clean \
  $MAVEN_PHASE \
  $MAVEN_ARGS


# Clean up
rm $STRATEGOXT_MIN_JAR
