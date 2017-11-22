#!/usr/bin/env bash

set -e

BRANCH=$1

apt-get update && apt-get install -yq --no-install-recommends openssh-client git-core
mkdir -p $HOME/.ssh && chmod 600 $HOME/.ssh
echo -n "${DEPLOY_KEY}" > $HOME/.ssh/id_rsa && chmod 600 $HOME/.ssh/id_rsa
ssh-keyscan -H auth.datashaman.com >> $HOME/.ssh/known_hosts
chmod 600 $HOME/.ssh/known_hosts
pip install dotenvy fabric jinja2
git clone -q https://github.com/datashaman/wifidog-auth-ops.git .ops
cd .ops && fab -H ubuntu@auth.datashaman.com deploy:${BRANCH}
