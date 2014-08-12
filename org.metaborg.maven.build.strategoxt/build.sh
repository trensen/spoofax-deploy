#!/usr/bin/env bash

set -e
set -u


# Parse input
while getopts ":ua:e:" opt; do
  case $opt in
    u)
      UPDATE_DISTRIB="true"
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

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

STRATEGOXT_DISTRIB_TAR="$DIR/strategoxt-distrib.tar"
STRATEGOXT_DISTRIB="$DIR/strategoxt-distrib/"
STRATEGOXT_JAR="$STRATEGOXT_DISTRIB/share/strategoxt/strategoxt/strategoxt.jar"
STRATEGOXT_MIN="$DIR/strategoxt-min"
STRATEGOXT_MIN_JAR="$DIR/strategoxt-min.jar"


# Update strategoxt distribution if it does not exist, or if requested
if [ -n "${UPDATE_DISTRIB+1}" ] || [ ! -f $STRATEGOXT_JAR ]; then
	rm -rf $STRATEGOXT_DISTRIB
  rm -f $STRATEGOXT_DISTRIB_TAR
	mkdir -p $STRATEGOXT_DISTRIB
	wget http://hydra.nixos.org/job/strategoxt-java/strategoxt-java-bootstrap/bootstrap3/latest/download-by-type/file/tar -O $STRATEGOXT_DISTRIB_TAR
	tar -xf $STRATEGOXT_DISTRIB_TAR -C $STRATEGOXT_DISTRIB
	chmod a+x "$STRATEGOXT_DISTRIB/share/strategoxt/macosx/"*
  chmod a+x "$STRATEGOXT_DISTRIB/share/strategoxt/linux/"*
	rm $STRATEGOXT_DISTRIB_TAR
	cd ..
fi


# Create minified strategoxt JAR
rm -rf $STRATEGOXT_MIN
mkdir -p $STRATEGOXT_MIN
unzip -qq -o -d $STRATEGOXT_MIN $STRATEGOXT_JAR
rm "$STRATEGOXT_MIN/run.class"
rm "$STRATEGOXT_MIN/start.class"
rm "$STRATEGOXT_MIN/COPYING"
rm "$STRATEGOXT_MIN/build.xml"
rm -rf "$STRATEGOXT_MIN/META-INF"
rm -rf "$STRATEGOXT_MIN/com"
rm -rf "$STRATEGOXT_MIN/fj"
rm -rf "$STRATEGOXT_MIN/jdbm"
rm -rf "$STRATEGOXT_MIN/jline"
rm -rf "$STRATEGOXT_MIN/org/metaborg"
rm -rf "$STRATEGOXT_MIN/org/spoofax"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/*.class"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/lang/*.class"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/lang/compat/*.class"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/lang/compat/override/*.class"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/lang/compat/stratego_rtg_compat"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/lang/compat/strc_compat"
rm -f $STRATEGOXT_MIN_JAR
jar cf $STRATEGOXT_MIN_JAR -C $STRATEGOXT_MIN .
rm -rf $STRATEGOXT_MIN


# Install strategoxt JARs and distribution into local maven repository
mvn \
  -f "$DIR/pom.xml" \
  clean install \
  $MAVEN_ARGS


# Clean up
rm $STRATEGOXT_MIN_JAR
