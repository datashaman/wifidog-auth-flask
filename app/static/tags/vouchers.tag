<vouchers>
    <h1>Vouchers</h1>

    <div class="actions-collection">
        <form class="pure-form" onsubmit={ create }>
            <fieldset>
                <input if={ hasRole('super-admin') } name="network" type="text" placeholder="NetworkID" required />
                <input if={ hasRole('super-admin') || hasRole('network-admin') } name="gateway" type="text" placeholder="GatewayID" required />
                <input name="minutes" type="number" min="0" step="30" value="60" required />
                <button type="submit" class="pure-button pure-button-primary">
                    <span class="oi" data-glyph="file" title="Create" aria-hidden="true"></span>
                    Create
                </button>
            </fieldset>
        </form>
    </div>

    <table if={ vouchers.length } width="100%" cellspacing="0" class="pure-table pure-table-horizontal">
        <thead>
            <tr>
                <th>ID</th>
                <th>A</th>
                <th>Minutes</th>
                <th>Created</th>
                <th>IP</th>
                <th>MAC</th>
                <th>Email</th>
                <th>Started</th>
                <th>Ends</th>

                <th class="actions">Actions</th>
            </tr>
        </thead>

        <tbody>
            <tr each={ row, i in vouchers } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
                <td>{ row['$id'] }</td>
                <td>{ row.active ? 'Y' : 'N' }</td>
                <td>{ render(row.minutes) }</td>
                <td>{ render(row.created_at) }</td>
                <td>{ render(row.ip) }</td>
                <td>{ render(row.mac) }</td>
                <td>{ render(row.email) }</td>
                <td>{ render(row.started_at) }</td>
                <td>{ render(calculateEndAt(row)) }</td>

                <td class="actions actions-row">
                    <button class="pure-button { row.active ? 'state-invalid' : 'state-valid' }" onclick={ toggleActive }>
                        <span if={ row.active }>
                            <span class="oi" data-glyph="x" title="Deactivate" aria-hidden="true"></span>
                            Deactivate
                        </span>
                        <span if={ !row.active }>
                            <span class="oi" data-glyph="check" title="Reactivate" aria-hidden="true"></span>
                            Reactivate
                        </span>
                    </button>
                </td>
            </tr>
        </tbody>
    </table>

    <script>
    var self = this;

    self.mixin('render');
    self.mixin('currentuser');

    self.vouchers = opts.vouchers;

    RiotControl.on('vouchers.loaded', function (vouchers) {
        self.vouchers = vouchers;
        self.update();
    });

    RiotControl.trigger('vouchers.load');

    pad(number, length) {
        var str = '' + number;

        while (str.length < length) {
            str = '0' + str;
        }

        return str;
    }

    renderDateTime(dt) {
        if (dt) {
            dt = new Date(dt.$date);
            return self.pad(dt.getHours(), 2) + ':' + self.pad(dt.getMinutes(), 2);
        }
    }

    calculateEndAt(row) {
        if (row.started_at) {
            var dt = new Date(row.started_at.$date);
            return {
                $date: new Date(dt.getTime() + row.minutes * 60000)
            };
        }
    }

    getVoucherId(e) {
        return $(e.target).closest('tr[data-id]').data('id');
    }

    create(e) {
        RiotControl.trigger('vouchers.create', {
            network: self.hasRole('super-admin') ? self.network.value : self.currentuser.network,
            gateway: self.hasRole('super-admin') || self.hasRole('network-admin') ? self.gateway.value : self.currentuser.gateway,
            minutes: parseInt(self.minutes.value)
        });
        return false;
    }

    toggleActive(e) {
        if(confirm('Are you sure?')) {
            RiotControl.trigger('voucher.toggle', self.getVoucherId(e));
        }
    }
    </script>
</vouchers>
