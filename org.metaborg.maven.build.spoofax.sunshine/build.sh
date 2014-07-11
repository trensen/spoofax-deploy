#!/bin/bash

set -e
set -u

MAVEN_OPTS="-Xmx1024m -Xms1024m -Xss32m -server -XX:+UseParallelGC" JAVA_HOME=$(/usr/libexec/java_home) mvn clean package
