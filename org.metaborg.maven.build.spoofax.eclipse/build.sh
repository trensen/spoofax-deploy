#!/bin/bash

set -e
set -u


# Parse input
while getopts ":gjpq:m:" opt; do
  case $opt in
    g)
      NO_GENERATOR="true"
      ;;
    j)
      NO_JAVA_PROJECTS="true"
      ;;
    p)
      NO_PLUGIN_PROJECTS="true"
      ;;
    q)
      INPUT_QUALIFIER=$OPTARG
      ;;
    m)
      INPUT_MAVEN_EXTRA_ARGS=$OPTARG
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
MVN_EXTRA_ARGS=${INPUT_MAVEN_EXTRA_ARGS:-""}

DIR=$(pwd)
ROOT="$DIR/../../"

STRATEGOXT_DISTRIB="$DIR/strategoxt-distrib"
STRATEGOXT_JAR="$STRATEGOXT_DISTRIB/share/strategoxt/strategoxt/strategoxt.jar"

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


# Build the generator
if [ -z ${NO_GENERATOR+x} ]; then
  cp -R $STRATEGOXT_DISTRIB "$GEN_LOC/strategoxt-distrib"
  cd $GEN_LOC
  ./build.sh
  cd $DIR
fi


# Copy strategoxt jar into java backend.
# TODO: get rid of this, it is hacky!
cp $STRATEGOXT_JAR "$ROOT/strategoxt/strategoxt/stratego-libraries/java-backend/java/strategoxt.jar"


# Minify strategoxt jar
mkdir -p strategoxt-min
tar xf $STRATEGOXT_JAR -C strategoxt-min
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
rm -rf strategoxt-min/org/strategoxt/lang
rm -rf strategoxt-min/org/strategoxt/strj
rm -rf strategoxt-min/org/strategoxt/tools
jar cf strategoxt-min.jar -C strategoxt-min .
rm -rf strategoxt-min


# Install strategoxt JARs into local maven repository
function maven-install-jar {
  JAVA_HOME=$(/usr/libexec/java_home) mvn install:install-file \
    -Dfile=$1 \
    -DgroupId=org.metaborg \
    -DartifactId=$2 \
    -Dversion=1.2.0-SNAPSHOT \
    -Dpackaging=jar
}

maven-install-jar $STRATEGOXT_JAR strategoxt-jar
maven-install-jar strategoxt-min.jar strategoxt-min-jar
rm strategoxt-min.jar


# Execute maven build for java and plugin projects
function maven {
  MVN_ARGS=$1
  MVN_FILE=$2

  MAVEN_OPTS="-Xmx1024m -Xms1024m -Xss32m -server -XX:+UseParallelGC" JAVA_HOME=$(/usr/libexec/java_home) mvn \
    -f $MVN_FILE \
    -DforceContextQualifier=$QUALIFIER \
    -Dstrategoxt-jar=$STRATEGOXT_JAR \
    -Ddist-loc=$GEN_DIST_LOC \
    -Dnative-loc=$NATIVE_LOC \
    $MVN_ARGS \
    $MVN_EXTRA_ARGS
}

if [ -z ${NO_JAVA_PROJECTS+x} ]; then
  maven "clean install" "java/pom.xml"
fi

if [ -z ${NO_PLUGIN_PROJECTS+x} ]; then
  maven "clean verify" "plugin/pom.xml"
fi
