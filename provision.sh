#!/usr/bin/env bash

sudo -H true

wget -qO- https://get.docker.com/ | sh

COMPOSE_VERSION=`git ls-remote https://github.com/docker/compose | grep refs/tags | grep -oP "[0-9]+\.[0-9][0-9]+\.[0-9]+$" | tail -n 1`
sudo -H sh -c "curl -L https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose"
sudo -H chmod +x /usr/local/bin/docker-compose
sudo -H sh -c "curl -L https://raw.githubusercontent.com/docker/compose/${COMPOSE_VERSION}/contrib/completion/bash/docker-compose > /etc/bash_completion.d/docker-compose"

sudo -H apt-get install sqlite3

git clone https://github.com/datashaman/wifidog-auth-host.git config

for config in config/*
do
  cd $config
  docker-compose pull
  cd -
done
