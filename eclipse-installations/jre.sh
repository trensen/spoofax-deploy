#!/usr/bin/env bash


# Error early
set -eu


# Exit on interruption
function terminate() { exit $?; }
trap terminate SIGINT


# Import common functionality
source common.sh


# Download and extract JRE's for supported platforms
downloadjre "macosx" "x86_64" "http://download.oracle.com/otn-pub/java/jdk/7u72-b14/jre-7u72-macosx-x64.tar.gz"
downloadjre "win32"  "x86_64" "http://download.oracle.com/otn-pub/java/jdk/7u72-b14/jre-7u72-windows-x64.tar.gz"
downloadjre "win32"  "x86"    "http://download.oracle.com/otn-pub/java/jdk/7u72-b14/jre-7u72-windows-i586.tar.gz"
downloadjre "linux"  "x86_64" "http://download.oracle.com/otn-pub/java/jdk/7u72-b14/jre-7u72-linux-x64.tar.gz"
downloadjre "linux"  "x86"    "http://download.oracle.com/otn-pub/java/jdk/7u72-b14/jre-7u72-linux-i586.tar.gz"
