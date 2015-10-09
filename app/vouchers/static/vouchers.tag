<vouchers>
    <h1>Vouchers</h1>

    <div class="actions-collection">
        <form class="pure-form" onsubmit={ create }>
            <fieldset>
                <input name="create_minutes" type="number" min="0" step="30" value="60" required />
                <button type="submit" class="pure-button pure-button-primary">
                    <span class="oi" data-glyph="file" title="Create" aria-hidden="true"></span>
                    Create
                </button>
                <button if={ vouchers.length > 1 } type="button" class="pure-button" onclick={ removeAll }>
                    <span class="oi" data-glyph="x" title="Remove All" aria-hidden="true"></span>
                    Remove All
                </button>
            </fieldset>
        </form>
    </div>

    <table if={ vouchers.length } width="100%" cellspacing="0" class="pure-table pure-table-horizontal">
        <thead>
            <tr>
                <th>ID</th>
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
                <td><a href="/wifidog/login?voucher={ row['$id'] }">{ row['$id'] }</a></td>
                <td>{ row.minutes }</td>
                <td>{ renderDateTime(row.created_at) }</td>
                <td>{ row.ip }</td>
                <td>{ row.mac }</td>
                <td>{ row.email }</td>
                <td>{ renderDateTime(row.started_at) }</td>
                <td>{ renderDateTime(calculateEndAt(row)) }</td>

                <td class="actions actions-row">
                    <button class="pure-button" onclick={ remove }>
                        <span class="oi" data-glyph="x" title="Remove" aria-hidden="true"></span>
                        Remove
                    </button>
                </td>
            </tr>
        </tbody>
    </table>

    <script>
    var self = this;
    self.vouchers = opts.vouchers;

    RiotControl.on('vouchers.updated', function (vouchers) {
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
            return new Date(dt.getTime() + row.minutes * 60000);
        }
    }

    getVoucherId(e) {
        return $(e.target).closest('tr[data-id]').data('id');
    }

    create(e) {
        RiotControl.trigger('vouchers.create', self.create_minutes.value);
        return false;
    }

    removeAll(e) {
        if(confirm('Are you sure?')) {
            RiotControl.trigger('vouchers.remove');
        }
    }

    remove(e) {
        if(confirm('Are you sure?')) {
            RiotControl.trigger('voucher.remove', self.getVoucherId(e));
        }
    }
    </script>
</vouchers>
