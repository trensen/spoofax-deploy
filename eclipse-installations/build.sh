#!/usr/bin/env bash


# Error early
set -eu


# Exit on interruption
function terminate() { exit $?; }
trap terminate SIGINT


# Import common functionality
source common.sh


# Create Eclipse installations for supported platforms
spoofax "macosx" "cocoa" "x86_64" "Eclipse.app/Contents/MacOS/eclipse.ini" "../../../jre/bin/java";
spoofax "macosx" "cocoa" "x86"    "Eclipse.app/Contents/MacOS/eclipse.ini" "../../../jre/bin/java";
spoofax "win32"  "win32" "x86_64" "eclipse.ini"                            "jre\\\bin\\\javaw.exe";
spoofax "win32"  "win32" "x86"    "eclipse.ini"                            "jre\\\bin\\\javaw.exe";
spoofax "linux"  "gtk"   "x86_64" "eclipse.ini"                            "jre/bin/java";
spoofax "linux"  "gtk"   "x86"    "eclipse.ini"                            "jre/bin/java"; 
