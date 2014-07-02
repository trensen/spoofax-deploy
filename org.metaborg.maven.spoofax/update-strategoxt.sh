#!/bin/bash

set -e
set -u

rm -rf strategoxt-distrib
mkdir strategoxt-distrib
cd strategoxt-distrib
wget http://hydra.nixos.org/job/strategoxt-java/strategoxt-java-bootstrap/bootstrap3/latest/download-by-type/file/tar -O strategoxt-distrib.tar
tar -xf strategoxt-distrib.tar
chmod a+x share/strategoxt/macosx/*
rm strategoxt-distrib.tar
cd ..
