<gateways>
    <h1>Gateways</h1>

    <div class="actions-collection">
        <form class="pure-form" onsubmit={ create }>
            <fieldset>
                <input if={ isSuperAdmin() } name="network" type="text" placeholder="NetworkID" required />
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
                <th if={ isSuperAdmin() }>Network</th>
                <th>ID</th>
                <th>Title</th>
                <th>Description</th>
                <th>Created At</th>

                <th class="actions">Actions</th>
            </tr>
        </thead>

        <tbody>
            <tr each={ row, i in gateways } data-id={ row.id } class={ pure-table-odd: i % 2 }>
                <td if={ isSuperAdmin() }>{ render(row.network) }</td>
                <td>{ render(row.id) }</td>
                <td>{ render(row.title) }</td>
                <td>{ render(row.description) }</td>
                <td>{ render(row.created_at) }</td>

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

    RiotControl.on('gateways.loaded', function (gateways) {
        self.gateways = gateways;
        self.update();
    });

    RiotControl.on('currentuser.loaded', function (currentuser) {
        self.currentuser = currentuser;
        self.update();
    });

    RiotControl.trigger('gateways.load');

    isSuperAdmin() {
        return self.currentuser.roles.indexOf('super-admin') > -1;
    }

    getId(e) {
        return $(e.target).closest('tr[data-id]').data('id');
    }

    create(e) {
        RiotControl.trigger('gateways.create', {
            network: self.isSuperAdmin() ? self.network.value : self.currentuser.network,
            id: self.id.value,
            title: self.title.value,
            description: self.description.value
        });
        return false;
    }

    remove(e) {
        if(confirm('Are you sure?')) {
            RiotControl.trigger('gateway.remove', self.getId(e));
        }
    }
    </script>
</gateways>
