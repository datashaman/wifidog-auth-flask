#!/usr/bin/env bash

tempdir=$(mktemp -d /tmp/auth-XXXXX)
BUILD_HOME=${BUILD_HOME:-$(pwd)/build}
(cd $tempdir; tar -xvf "$BUILD_HOME/build.tgz")
pip install --force-reinstall --ignore-installed --upgrade --no-index --no-deps $tempdir/*
