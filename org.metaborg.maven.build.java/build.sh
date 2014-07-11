#!/bin/bash

set -e
set -u


# Parse input
while getopts ":gq:" opt; do
  case $opt in
    g)
      NO_GENERATOR="true"
      ;;
    q)
      INPUT_QUALIFIER=$OPTARG
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

DIR=$(pwd)
ROOT="$DIR/../../"
GEN_LOC="$ROOT/spoofax/org.strategoxt.imp.generator/"
GEN_DIST_LOC="$GEN_LOC/dist/"


# Copy strategoxt JAR and distribution from (local) Maven repository
function maven-get {
  JAVA_HOME=$(/usr/libexec/java_home) mvn org.apache.maven.plugins:maven-dependency-plugin:2.8:get \
    -Dartifact=$1 \
    -Ddest=$2 \
    -Dtransitive=false \
    -q
}

maven-get org.metaborg:strategoxt-jar:1.2.0-SNAPSHOT strategoxt.jar
rm -rf strategoxt-distrib
mkdir -p strategoxt-distrib
maven-get org.metaborg:strategoxt-distrib:1.2.0-SNAPSHOT:tar:bin strategoxt-distrib/distrib.tar
cd strategoxt-distrib
tar -xf distrib.tar
chmod a+x share/strategoxt/macosx/*
rm distrib.tar
cd ..


# Build the generator
if [ -z ${NO_GENERATOR+x} ]; then
  rm -rf "$GEN_LOC/strategoxt-distrib"
  cp -r strategoxt-distrib "$GEN_LOC/strategoxt-distrib"
  cd "$GEN_LOC"
  ./build.sh
  cd "$DIR"
fi


# Copy strategoxt jar into strategoxt java backend
cp strategoxt.jar ../../strategoxt/strategoxt/stratego-libraries/java-backend/java/strategoxt.jar


# Build and install Java projects
MAVEN_OPTS="-Xmx1024m -Xms1024m -Xss32m -server -XX:+UseParallelGC" JAVA_HOME=$(/usr/libexec/java_home) mvn \
  -DforceContextQualifier=$QUALIFIER \
  clean install


# Clean up
rm strategoxt.jar
rm -rf strategoxt-distrib
