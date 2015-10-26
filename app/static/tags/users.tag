<users>
    <div class="header">
        <h1>Users</h1>

        <div class="actions-collection">
            <form class="pure-form" onsubmit={ create }>
                <fieldset>
                    <input if={ hasRole('super-admin') } name="network" type="text" placeholder="NetworkID" required />
                    <input if={ hasRole('super-admin') || hasRole('network-admin') } name="gateway" type="text" placeholder="GatewayID" required />
                    <input name="email" type="text" placeholder="Email" required />
                    <input name="password" type="text" placeholder="Password" required />
                    <button type="submit" class="pure-button pure-button-primary">
                        <span class="oi" data-glyph="file" title="Create" aria-hidden="true"></span>
                        Create
                    </button>
                </fieldset>
            </form>
        </div>
    </div>

    <div class="content">
        <table if={ rows.length } width="100%" cellspacing="0" class="pure-table pure-table-horizontal">
            <thead>
                <tr>
                    <th if={ hasRole('super-admin') }>Network</th>
                    <th if={ hasRole('super-admin') || hasRole('network-admin') }>Gateway</th>
                    <th>Roles</th>
                    <th>Email</th>
                    <th>Created</th>
                    <th class="actions">Actions</th>
                </tr>
            </thead>

            <tbody>
                <tr each={ row, i in rows } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
                    <td if={ hasRole('super-admin') } data-label="Network">{ row.network ? render(row.network) : 'Any' }</td>
                    <td if={ hasRole('super-admin') || hasRole('network-admin') } data-label="Gateway">{ row.gateway ? render(row.gateway) : 'Any' }</td>
                    <td data-label="Roles">{ render(row.roles) }</td>
                    <td data-label="Email">{ render(row.email) }</td>
                    <td data-label="Created At">{ render(row.created_at) }</td>

                    <td class="actions actions-row">
                        <button class="pure-button" onclick={ remove } disabled={ currentuser.id == row['$id'] } title={ currentuser.id == row['$id'] ? 'Cowardly refuse to remove current user' : '' }>
                            <span class="oi" data-glyph="x" title="Remove" aria-hidden="true"></span>
                            Remove
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    this.mixin('render');
    this.mixin('currentuser');

    var self = this;

    RiotControl.on('users.loaded', function (users) {
        self.rows = users;
        self.update();
    });

    RiotControl.trigger('users.load');

    getId(e) {
        return $(e.target).closest('tr[data-id]').data('id');
    }

    create(e) {
        RiotControl.trigger('users.create', {
            network: self.hasRole('super-admin') ? self.network.value : self.currentuser.network,
            gateway: self.hasRole('super-admin') || self.hasRole('network-admin') ? self.gateway.value : self.currentuser.gateway,
            email: self.email.value,
            password: self.password.value
        });
        return false;
    }

    removeAll(e) {
        if(confirm('Are you sure?')) {
            RiotControl.trigger('users.remove');
        }
    }

    remove(e) {
        if(confirm('Are you sure?')) {
            RiotControl.trigger('user.remove', self.getId(e));
        }
    }
</users>
