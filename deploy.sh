#!/usr/bin/env bash

python3 -V
pip3 -V

tempdir=$(mktemp -d /tmp/auth-XXXXX)
BUILD_HOME=${BUILD_HOME:-$(pwd)/build}
(cd $tempdir; tar -xvf "$BUILD_HOME/build.tgz")
pip3 install --force-reinstall --ignore-installed --upgrade --no-index --no-deps $tempdir/*
