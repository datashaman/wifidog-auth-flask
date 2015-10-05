from app import db, manager
from flask.ext.script import prompt, prompt_pass

from app.gateways import Gateway
from app.networks.config import NETWORKS
from app.networks.models import Network

@manager.command
def seed_networks():
    if Network.query.count() == 0:
        for network_id, defn in NETWORKS.iteritems():
            network = Network(id=network_id, title=defn['title'], description=defn['description'])
            db.session.add(network)

            for gateway_id, gateway_defn in defn['gateways'].iteritems():
                gateway_defn['id'] = gateway_id
                gateway_defn['network_id'] = network_id
                gateway = Gateway(**gateway_defn)
                db.session.add(gateway)

        db.session.commit()
