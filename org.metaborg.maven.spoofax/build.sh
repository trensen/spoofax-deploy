#!/bin/bash

set -e
set -u

# Set build vars
MVN_EXTRA_ARGS=${1:-""}
DIR=$(pwd)
ROOT="$DIR/../../"
STRATEGOXT_DISTRIB="$DIR/strategoxt-distrib"
STRATEGOXT_JAR="$STRATEGOXT_DISTRIB/share/strategoxt/strategoxt/strategoxt.jar"
NATIVE_LOC="$ROOT/spoofax/org.strategoxt.imp.nativebundle/native/macosx/"
GEN_LOC="$ROOT/spoofax/org.strategoxt.imp.generator/"

# Build the generator
cp -R $STRATEGOXT_DISTRIB "$GEN_LOC/strategoxt-distrib"
cd $GEN_LOC
./build.sh
cd $DIR

GEN_DIST_LOC="$GEN_LOC/dist/"
ASTER_JAR="$GEN_DIST_LOC/aster.jar"
SDF2IMP_JAR="$GEN_DIST_LOC/sdf2imp.jar"
MAKE_PERMISSIVE_JAR="$GEN_DIST_LOC/make_permissive.jar"

# Copy strategoxt.jar into java-backend
cp $STRATEGOXT_JAR "$ROOT/strategoxt/strategoxt/stratego-libraries/java-backend/java/strategoxt.jar"

# Build Spoofax
MAVEN_OPTS="-Xmx1024m -Xms1024m -Xss32m -server -XX:+UseParallelGC" JAVA_HOME=$(/usr/libexec/java_home) mvn \
  -Ddist-loc=$GEN_DIST_LOC \
  -Dnative-loc=$NATIVE_LOC \
  -Daster-jar=$ASTER_JAR \
  -Dsdf2imp-jar=$SDF2IMP_JAR \
  -Dmakepermissive-jar=$MAKE_PERMISSIVE_JAR \
  -Dstrategoxt-jar=$STRATEGOXT_JAR \
  clean verify \
  $MVN_EXTRA_ARGS
