from fabric import *
from fabric.contrib.files import *

commit = '0.5.0'

def deploy():
    with run('source /home/ubuntu/.nvm/nvm.sh'), cd('/var/www/auth'):
        run('nvm use')
        run('git remote update -p')
        run('git checkout %s' % commit)
        run('make production-install')
