#!/usr/bin/env bash

/usr/bin/curl "http://localhost:${VIRTUAL_PORT}/?auth_token=${AUTH_TOKEN}" || exit 1
