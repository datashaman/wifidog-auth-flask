<gateways>
    <h1>Gateways</h1>

    <div class="actions-collection">
        <form class="pure-form" onsubmit={ create }>
            <fieldset>
                <input name="id" type="text" placeholder="GatewayID" required />
                <input name="title" type="text" placeholder="Title" required />
                <input name="description" type="text" placeholder="Description" required />
                <button type="submit" class="pure-button pure-button-primary">
                    <span class="oi" data-glyph="file" title="Create" aria-hidden="true"></span>
                    Create
                </button>
            </fieldset>
        </form>
    </div>

    <table if={ gateways.length } width="100%" cellspacing="0" class="pure-table pure-table-horizontal">
        <thead>
            <tr>
                <th>ID</th>
                <th>Network</th>
                <th>Title</th>
                <th>Description</th>
                <th>Created At</th>

                <th class="actions">Actions</th>
            </tr>
        </thead>

        <tbody>
            <tr each={ row, i in gateways } data-id={ row.id } class={ pure-table-odd: i % 2 }>
                <td>{ row.network_id }</td>
                <td>{ row.id }</td>
                <td>{ row.title }</td>
                <td>{ row.description }</td>
                <td>{ renderDateTime(row.created_at) }</td>

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
    self.gateways = opts.gateways;

    RiotControl.on('gateways.updated', function (gateways) {
        self.gateways = gateways;
        self.update();
    });

    RiotControl.trigger('gateways.load');

    renderDateTime(dt) {
        if (dt) {
            dt = new Date(dt);
            return dt.toLocaleString();
        }
    }

    getId(e) {
        return $(e.target).closest('tr[data-id]').data('id');
    }

    create(e) {
        RiotControl.trigger('gateways.create', self.id.value, self.title.value, self.description.value);
        return false;
    }

    remove(e) {
        if(confirm('Are you sure?')) {
            RiotControl.trigger('gateway.remove', self.getId(e));
        }
    }
    </script>
</gateways>
