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

GEN_DIST_LOC="$GEN_LOC/dist/"
ASTER_JAR="$GEN_DIST_LOC/aster.jar"
SDF2IMP_JAR="$GEN_DIST_LOC/sdf2imp.jar"
MAKE_PERMISSIVE_JAR="$GEN_DIST_LOC/make_permissive.jar"


# Copy strategoxt.jar into java-backend
cp $STRATEGOXT_JAR "$ROOT/strategoxt/strategoxt/stratego-libraries/java-backend/java/strategoxt.jar"


function maven {
  MVN_ARGS=$1
  MVN_FILE=$2

  MAVEN_OPTS="-Xmx1024m -Xms1024m -Xss32m -server -XX:+UseParallelGC" JAVA_HOME=$(/usr/libexec/java_home) mvn \
    -f $MVN_FILE \
    -DforceContextQualifier=$QUALIFIER \
    -Ddist-loc=$GEN_DIST_LOC \
    -Dnative-loc=$NATIVE_LOC \
    -Daster-jar=$ASTER_JAR \
    -Dsdf2imp-jar=$SDF2IMP_JAR \
    -Dmakepermissive-jar=$MAKE_PERMISSIVE_JAR \
    -Dstrategoxt-jar=$STRATEGOXT_JAR \
    $MVN_ARGS \
    $MVN_EXTRA_ARGS
}


# Build and install Java projects
if [ -z ${NO_JAVA_PROJECTS+x} ]; then
  maven "clean install" "java/pom.xml"
fi

# Build Spoofax
if [ -z ${NO_PLUGIN_PROJECTS+x} ]; then
  maven "clean verify" "plugin/pom.xml"
fi
