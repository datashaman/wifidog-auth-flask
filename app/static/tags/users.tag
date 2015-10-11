<users>
    <h1>Users</h1>

    <div class="actions-collection">
        <form class="pure-form" onsubmit={ create }>
            <fieldset>
                <input if={ isSuperAdmin() } name="network" type="text" placeholder="NetworkID" required />
                <input if={ isSuperAdmin() || isNetworkAdmin() } name="gateway" type="text" placeholder="GatewayID" required />
                <input name="email" type="text" placeholder="Email" required />
                <input name="password" type="text" placeholder="Password" required />
                <button type="submit" class="pure-button pure-button-primary">
                    <span class="oi" data-glyph="file" title="Create" aria-hidden="true"></span>
                    Create
                </button>
                <button if={ users.length > 1 } type="button" class="pure-button" onclick={ removeAll }>
                    <span class="oi" data-glyph="x" title="Remove All" aria-hidden="true"></span>
                    Remove All
                </button>
            </fieldset>
        </form>
    </div>

    <table if={ users.length } width="100%" cellspacing="0" class="pure-table pure-table-horizontal">
        <thead>
            <tr>
                <th if={ isSuperAdmin() }>Network</th>
                <th if={ isSuperAdmin() || isNetworkAdmin() }>Gateway</th>
                <th>Email</th>
                <th>Created</th>
                <th class="actions">Actions</th>
            </tr>
        </thead>

        <tbody>
            <tr each={ row, i in users } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
                <td if={ isSuperAdmin() }>{ render(row.network) }</td>
                <td if={ isSuperAdmin() || isNetworkAdmin() }>{ render(row.gateway) }</td>
                <td>{ render(row.email) }</td>
                <td>{ render(row.created_at) }</td>

                <td class="actions actions-row">
                    <button class="pure-button" onclick={ remove } disabled={ currentuser.id == row['$id'] } title={ currentuser.id == row['$id'] ? 'Cowardly refuse to remove current user' : '' }>
                        <span class="oi" data-glyph="x" title="Remove" aria-hidden="true"></span>
                        Remove
                    </button>
                </td>
            </tr>
        </tbody>
    </table>

    <script>
    var self = this;

    RiotControl.on('users.loaded', function (users) {
        self.users = users;
        self.update();
    });

    RiotControl.on('currentuser.loaded', function (currentuser) {
        self.currentuser = currentuser;
        self.update();
    });

    RiotControl.trigger('users.load');

    isSuperAdmin() {
        return self.currentuser.roles.indexOf('super-admin') > -1;
    }

    isNetworkAdmin() {
        return self.currentuser.roles.indexOf('network-admin') > -1;
    }

    getId(e) {
        return $(e.target).closest('tr[data-id]').data('id');
    }

    create(e) {
        RiotControl.trigger('users.create', {
            network: self.isSuperAdmin() ? self.network.value : self.currentuser.network,
            gateway: self.isSuperAdmin() || self.isNetworkAdmin() ? self.gateway.value : self.currentuser.gateway,
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
    </script>
</users>
