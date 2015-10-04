from app import db, manager

@manager.command
def expire_vouchers():
    # Vouchers that are in use and have expired
    sql = "delete from vouchers where datetime(started_at, '+' || minutes || ' minutes') < current_timestamp"
    db.engine.execute(text(sql))
    
    # Old vouchers that have not been used yet
    sql = "delete from vouchers where datetime(created_at, '+' || %d || ' minutes') < current_timestamp and started_at is null" % app.config.get('VOUCHER_MAXAGE', 120)
    db.engine.execute(text(sql))
