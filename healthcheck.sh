#!/usr/bin/env bash

curl http://localhost:$VIRTUAL_PORT/?auth_token=$AUTH_TOKEN || exit 1
