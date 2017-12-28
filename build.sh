#!/usr/bin/env bash

tempdir=$(mktemp -d /tmp/auth-XXXXX)
pip3 wheel -r requirements/production.txt --wheel-dir=$tempdir
BUILD_HOME=${BUILD_HOME:-$(pwd)/build}
mkdir -p "$BUILD_HOME"
(cd "$tempdir"; tar -czvf "$BUILD_HOME/build.tgz" *)