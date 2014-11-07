#!/usr/bin/env bash

set -e
set -u

STRATEGOXT_DISTRIB_TAR="$1"
STRATEGOXT_DISTRIB="$2"

rm -rf $STRATEGOXT_DISTRIB
rm -f $STRATEGOXT_DISTRIB_TAR
mkdir -p $STRATEGOXT_DISTRIB
wget http://hydra.nixos.org/job/strategoxt-java/strategoxt-java-bootstrap/bootstrap3/latest/download-by-type/file/tar -O $STRATEGOXT_DISTRIB_TAR
tar -xf $STRATEGOXT_DISTRIB_TAR -C $STRATEGOXT_DISTRIB
chmod a+x "$STRATEGOXT_DISTRIB/share/strategoxt/macosx/"*
chmod a+x "$STRATEGOXT_DISTRIB/share/strategoxt/linux/"*
rm $STRATEGOXT_DISTRIB_TAR
cd ..