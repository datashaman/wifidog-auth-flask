import json

from app.graphs import states
from app.models import Change, db

class VoucherAdmin(object):
    def workflow(self, user, voucher, event, **args):
        if voucher.status in states:
            source_status = voucher.status
            state = states[source_status]

            if event in state:
                voucher.status = state[event]

                for key, value in args.iteritems():
                    setattr(voucher, key, value)

                change = Change()
                change.changed_type = 'Voucher'
                change.changed_id = voucher.id
                change.event = event
                change.source = source_status
                change.destination = voucher.status
                change.args = json.dumps(args)
                change.user_id = user.id

                db.session.add(change)
                db.session.commit()
            else:
                raise Exception('%s is not valid for %s vouchers: you may only %s' % (event, voucher.status, state.keys()))
        else:
            raise Exception('%s is not valid' % voucher.status)
