from fabric import *
from fabric.contrib.files import *

env.forward_agent = True

dirname = os.path.dirname(os.path.realpath(__file__))

commit = 'develop'

def deploy():
    with cd('/var/www/auth'):
        run('git remote update -p')

        run('git checkout %s' % commit)
        run('git pull --ff-only')

        with prefix('source /home/ubuntu/.virtualenvs/auth/bin/activate'):
            with prefix('source /home/ubuntu/.nvm/nvm.sh'), prefix('nvm use'):
                run('make production-install')

            run('make db-upgrade')

        upload_template('fabric/supervisor/auth.conf', '/etc/supervisor/conf.d', template_dir=dirname, context=env, use_sudo=True, use_jinja=True)

        sudo('supervisorctl reread')
        sudo('supervisorctl update')
        sudo('supervisorctl restart auth')
