#!/usr/bin/env bash


# Error early
set -eu


# Exit on interruption
function terminate() { exit $?; }
trap terminate SIGINT


# Import common functionality
source common.sh


# Mirror update sites for faster creation of Eclipse installations
mirror $ECLIPSE_UPDATE_SITE $ECLIPSE_UPDATE_MIRROR
mirror $SPOOFAX_UPDATE_SITE $SPOOFAX_UPDATE_MIRROR
