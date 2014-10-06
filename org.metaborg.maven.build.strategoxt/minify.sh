#!/usr/bin/env bash

set -e
set -u

STRATEGOXT_JAR="$1"
STRATEGOXT_MIN="$2"
STRATEGOXT_MIN_JAR="$3"

rm -rf $STRATEGOXT_MIN
mkdir -p $STRATEGOXT_MIN
unzip -qq -o -d $STRATEGOXT_MIN $STRATEGOXT_JAR
rm "$STRATEGOXT_MIN/run.class"
rm "$STRATEGOXT_MIN/start.class"
rm "$STRATEGOXT_MIN/COPYING"
rm "$STRATEGOXT_MIN/build.xml"
rm -rf "$STRATEGOXT_MIN/META-INF"
rm -rf "$STRATEGOXT_MIN/com"
rm -rf "$STRATEGOXT_MIN/net"
rm -rf "$STRATEGOXT_MIN/fj"
rm -rf "$STRATEGOXT_MIN/jdbm"
rm -rf "$STRATEGOXT_MIN/jline"
rm -rf "$STRATEGOXT_MIN/etc"
rm -rf "$STRATEGOXT_MIN/org/metaborg"
rm -rf "$STRATEGOXT_MIN/org/spoofax"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/"*".class"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/lang/"*".class"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/lang/compat/"*".class"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/lang/compat/override/"*".class"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/lang/compat/stratego_rtg_compat"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/lang/compat/strc_compat"
rm -rf "$STRATEGOXT_MIN/org/strategoxt/lang/parallel"
rm -f $STRATEGOXT_MIN_JAR
jar cf $STRATEGOXT_MIN_JAR -C $STRATEGOXT_MIN -J-Xmx512m .
rm -rf $STRATEGOXT_MIN