#!/usr/bin/env bash

set -e
set -u


# Parse input
while getopts ":uda:e:" opt; do
  case $opt in
    u)
      UPDATE_DISTRIB="true"
      ;;
    d)
      INPUT_MAVEN_DEPLOY="deploy"
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
MAVEN_ARGS=${INPUT_MAVEN_ARGS:-""}
if [ -z ${INPUT_MAVEN_ENV+x} ]; then
  export MAVEN_OPTS="-Xmx512m -Xms512m -Xss16m"
else
  export MAVEN_OPTS="$INPUT_MAVEN_ENV"
fi
MAVEN_DEPLOY=${INPUT_MAVEN_DEPLOY:-""}

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


# Install strategoxt JARs and distribution into local maven repository
mvn \
  -f "$DIR/pom.xml" \
  clean install \
  $MAVEN_DEPLOY \
  $MAVEN_ARGS
  
mvn \
  -f "$DIR/morepoms/strategoxt-jar/pom.xml" \
  clean install \
  $MAVEN_DEPLOY \
  $MAVEN_ARGS

mvn \
  -f "$DIR/morepoms/strategoxt-min-jar/pom.xml" \
  clean install \
  $MAVEN_DEPLOY \
  $MAVEN_ARGS


# Clean up
rm $STRATEGOXT_MIN_JAR
