#!/usr/bin/env bash

set -e
set -u

MAVEN_OPTS="-Xmx1024m -Xms1024m -Xss32m -server -XX:+UseParallelGC" mvn clean verify
