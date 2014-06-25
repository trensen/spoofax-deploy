#!/bin/bash

set -e
set -u

MVN_EXTRA_ARGS=${1:-""}

# TODO: build the generator
# TODO: copy strategoxt.jar into strj project


PWD=$(pwd)
DIST_LOC="$PWD/../../spoofax/org.strategoxt.imp.generator/dist/"
NATIVE_LOC="$PWD/../../spoofax/org.strategoxt.imp.nativebundle/native/macosx/"

ASTER_JAR="$DIST_LOC/aster.jar"
SDF2IMP_JAR="$DIST_LOC/sdf2imp.jar"
MAKE_PERMISSIVE_JAR="$DIST_LOC/make_permissive.jar"
STRATEGOXT_JAR="$PWD/../../strategoxt/strategoxt/stratego-libraries/java-backend/java/strategoxt.jar"


MAVEN_OPTS="-Xmx1024m -Xms1024m -Xss32m -server -XX:+UseParallelGC" JAVA_HOME=$(/usr/libexec/java_home) mvn \
  -Ddist-loc=$DIST_LOC \
  -Dnative-loc=$NATIVE_LOC \
  -Daster-jar=$ASTER_JAR \
  -Dsdf2imp-jar=$SDF2IMP_JAR \
  -Dmakepermissive-jar=$MAKE_PERMISSIVE_JAR \
  -Dstrategoxt-jar=$STRATEGOXT_JAR \
  clean verify \
  $MVN_EXTRA_ARGS
