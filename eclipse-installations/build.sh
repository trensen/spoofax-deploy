#!/usr/bin/env bash


# Error early
set -eu


# Exit on interruption
function terminate() { exit $?; }
trap terminate SIGINT


# Import common functionality
source common.sh


# Create Eclipse installations for supported platforms
spoofax "macosx" "cocoa" "x86_64" "Eclipse.app/Contents/MacOS/eclipse.ini" "../../../jre/Contents/Home/bin/java";
spoofax "win32"  "win32" "x86_64" "eclipse.ini"                            "jre\\\bin\\\server\\\jvm.dll";
spoofax "win32"  "win32" "x86"    "eclipse.ini"                            "jre\\\bin\\\client\\\jvm.dll";
spoofax "linux"  "gtk"   "x86_64" "eclipse.ini"                            "jre/bin/java";
spoofax "linux"  "gtk"   "x86"    "eclipse.ini"                            "jre/bin/java";
