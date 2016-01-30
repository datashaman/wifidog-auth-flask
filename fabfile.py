from fabric import *
from fabric.contrib.files import *

dirname = os.path.dirname(os.path.realpath(__file__))

commit = 'develop'

def deploy():
    with run('source /home/ubuntu/.nvm/nvm.sh'), cd('/var/www/auth'):
        run('nvm use')
        run('git remote update -p')
        run('git checkout %s' % commit)
        run('make production-install')
        run('make db-upgrade')

        upload_template('fabric/supervisor/auth.conf', '/etc/supervisor/conf.d', template_dir=dirname, context=env, use_sudo=True, use_jinja=True)
        sudo('supervisorctl reread')
        sudo('supervisorctl update')
