<vouchers>
    <div class="header">
        <h1>Vouchers</h1>

        <div class="actions-collection">
            <a href="/new-voucher" class="pure-button pure-button-primary">
                <span class="oi" data-glyph="file" title="New Voucher" aria-hidden="true"></span>
                New Voucher
            </a>
        </div>
    </div>

    <div class="content">
        <table if={ vouchers.length } id="vouchers" width="100%" cellspacing="0" class="pure-table pure-table-horizontal">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>S</th>
                    <th>Times</th>
                    <th>Minutes Left</th>

                    <th class="actions">Actions</th>
                </tr>
            </thead>

            <tbody>
                <tr each={ row, i in vouchers } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
                    <td class="id" data-label="ID">{ row['$id'] }</td>
                    <td class="status" data-label="Status"><span class="oi" data-glyph={ statusIcons[row.status] } title={ row.status } aria-hidden="true"></span></td>
                    <td data-label="Times">{ renderTimes(row) }</td>
                    <td data-label="Minutes Left">{ row.status == 'active' ? render(row.time_left) + '/' : '' }{ render(row.minutes) }</td>

                    <td class="actions actions-row">
                        <button class="pure-button" each={ action, defn in row.available_actions } value={ action } title={ action } onclick={ handleAction }>
                            <span if={ defn.icon } class="oi" data-glyph={ defn.icon } aria-hidden="true"></span>
                            { action }
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    var self = this;

    self.mixin('render');
    self.mixin('currentuser');

    self.vouchers = [];

    self.statusIcons = {
        new: 'file',
        active: 'bolt',
        ended: 'flag',
        expired: 'circle-x',
        archived: 'trash',
        blocked: 'thumb-down'
    };

    RiotControl.on('vouchers.loaded', function (vouchers) {
        self.vouchers = vouchers;
        self.update();
    });

    RiotControl.trigger('vouchers.load');

    calculateEndAt(row) {
        if (row.started_at) {
            var dt = new Date(row.started_at.$date);
            return {
                $date: new Date(dt.getTime() + row.minutes * 60000)
            };
        }
    }

    renderTimes(row) {
        var result = self.renderTime(row.created_at);

        if (row.started_at) {
            result += ' ' + self.renderTime(row.started_at);
            result += ' ' + self.renderTime(self.calculateEndAt(row));
        }

        return result;
    }

    handleAction(e) {
        var action = $(e.target).val(),
            id = self.getId(e);

        console.log('voucher', action, id);

        switch(action) {
        case 'delete':
        case 'archive':
            if(confirm('Are you sure?')) {
                RiotControl.trigger('voucher.' + action, id);
            }
            break;
        default:
            RiotControl.trigger('voucher.' + action, id);
        }
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
</vouchers>
