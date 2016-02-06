import dotenv
import os

from fabric import *
from fabric.contrib.files import *

env.dotenv_path = '/var/www/auth/.env'
env.forward_agent = True

template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fabric')

commit = 'develop'

@tqsk
def config(action=None, key=None, value=None):
    run('touch %(dotenv_path)s' % env)
    command = get_cli_string(env.dotenv_path, action, key, value)
    run(command)

@task
def deploy():
    with cd('/var/www/auth'):
        run('git remote update -p')

        run('git checkout %s' % commit)
        run('git pull --ff-only')

        upload_template('env/%s' % env.host, '.env', template_dir=template_dir, context=env, use_sudo=True, use_jinja=True)

        with prefix('source /home/ubuntu/.virtualenvs/auth/bin/activate'):
            with prefix('source /home/ubuntu/.nvm/nvm.sh'), prefix('nvm use'):
                run('make production-install')

            run('make db-upgrade')

        # Load host-based environment variables into env
        with open(os.path.join(template_dir, 'fabric/env/%s' % env.host)) as env_file:
            env.environment = {}

            for line in env_file:
                (key, value) = line.strip().split('=', 1)
                env.environment[key] = value

        upload_template('supervisor/auth.conf', '/etc/supervisor/conf.d', template_dir=template_dir, context=env, use_sudo=True, use_jinja=True)

        sudo('supervisorctl reread')
        sudo('supervisorctl update')
        sudo('supervisorctl restart auth')
