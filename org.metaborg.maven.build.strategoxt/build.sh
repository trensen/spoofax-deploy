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


# Set build variables
MAVEN_ARGS=${INPUT_MAVEN_ARGS:-""}
if [ -z ${INPUT_MAVEN_ENV+x} ]; then
  export MAVEN_OPTS="-Xmx512m -Xms512m -Xss16m"
fi

STRATEGOXT_JAR="strategoxt-distrib/share/strategoxt/strategoxt/strategoxt.jar"


# Update strategoxt distribution if it does not exist, or if requested
if [ -n "${UPDATE_DISTRIB+1}" ] || [ ! -f $STRATEGOXT_JAR ]; then
	rm -rf strategoxt-distrib
	mkdir strategoxt-distrib
	cd strategoxt-distrib
	wget http://hydra.nixos.org/job/strategoxt-java/strategoxt-java-bootstrap/bootstrap3/latest/download-by-type/file/tar -O strategoxt-distrib.tar
	tar -xf strategoxt-distrib.tar
	chmod a+x share/strategoxt/macosx/*
  chmod a+x share/strategoxt/linux/*
	rm strategoxt-distrib.tar
	cd ..
fi


# Create minified strategoxt JAR
rm -rf strategoxt-min
mkdir -p strategoxt-min
unzip -qq -o -d strategoxt-min/ strategoxt-distrib/share/strategoxt/strategoxt/strategoxt.jar
rm strategoxt-min/run.class
rm strategoxt-min/start.class
rm strategoxt-min/COPYING
rm strategoxt-min/build.xml
rm -rf strategoxt-min/META-INF
rm -rf strategoxt-min/com
rm -rf strategoxt-min/fj
rm -rf strategoxt-min/jdbm
rm -rf strategoxt-min/jline
rm -rf strategoxt-min/org/metaborg
rm -rf strategoxt-min/org/spoofax
rm -rf strategoxt-min/org/strategoxt/*.class
rm -rf strategoxt-min/org/strategoxt/lang/*.class
rm -rf strategoxt-min/org/strategoxt/lang/compat/*.class
rm -rf strategoxt-min/org/strategoxt/lang/compat/override/*.class
rm -rf strategoxt-min/org/strategoxt/lang/compat/stratego_rtg_compat
rm -rf strategoxt-min/org/strategoxt/lang/compat/strc_compat
rm -f strategoxt-min.jar
jar cf strategoxt-min.jar -C strategoxt-min .
rm -rf strategoxt-min


# Install strategoxt JARs and distribution into local maven repository
mvn clean install $MAVEN_ARGS


# Clean up
rm strategoxt-min.jar
