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
                <th>S</th>
                <th>Times</th>
                <th>IP</th>
                <th>MAC</th>
                <th>Email</th>
                <th>Minutes</th>

                <th class="actions">Actions</th>
            </tr>
        </thead>

        <tbody>
            <tr each={ row, i in vouchers } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
                <td>{ row['$id'] }</td>
                <td><span class="oi" data-glyph={ statusIcons[row.status] } title={ row.status } aria-hidden="true"></span></td>
                <td>{ renderTimes(row) }</td>
                <td>{ render(row.ip) }</td>
                <td>{ render(row.mac) }</td>
                <td>{ render(row.email) }</td>
                <td>{ render(row.minutes) }</td>

                <td class="actions actions-row">
                    <button class="pure-button" each={ event, defn in row.events } value={ event } title={ event } onclick={ action(event) }>
                        <span if={ defn.icon } class="oi" data-glyph={ defn.icon } aria-hidden="true"></span>
                        { event }
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

    self.statusIcons = {
        new: 'file',
        started: 'bolt',
        finished: 'flag',
        expired: 'circle-x',
        deleted: 'trash'
    };

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

    renderTime(dt) {
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

    extend(e) {
        RiotControl.trigger('voucher.extend', self.getId(e));
        return false;
    }

    renderTimes(row) {
        var result = self.renderTime(row.created_at);

        if (row.started_at) {
            result += ' / ' + self.renderTime(row.started_at);
            result += ' / ' + self.renderTime(self.calculateEndAt(row));
        }

        return result;
    }

    action(event) {
        return function(e) {
            $.ajax({
                type: 'POST',
                url: '/api/vouchers/' + self.getId(e) + '/' + event
            }).done(function() {
                console.log(arguments);
            }).fail(function() {
                console.error(arguments);
            });
        }.bind(this);
    }

    getId(e) {
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
