<gateways>
    <modal heading={ modal.heading } hidden={ modal.hidden } dismissable="true" onclose={ cancel }>
        <form class="pure-form pure-form-stacked" onsubmit={ doNothing }>
            <input type="hidden" id="original_id" class="pure-input-1" value={ parent.gateway['$id'] } />

            <div class="pure-menu pure-menu-horizontal">
                <ul class="pure-menu-list">
                    <li class="pure-menu-item { 'pure-menu-selected': parent.modal.active == 'basics' }"><a href="#" onclick={ parent.showTab('basics') } class="pure-menu-link">Basics</a></li>
                    <li class="pure-menu-item { 'pure-menu-selected': parent.modal.active == 'contact' }"><a href="#" onclick={ parent.showTab('contact') } class="pure-menu-link">Contact</a></li>
                    <li class="pure-menu-item { 'pure-menu-selected': parent.modal.active == 'social' }"><a href="#" onclick={ parent.showTab('social') } class="pure-menu-link">Social</a></li>
                </ul>
            </div>

            <div if={ parent.modal.active == 'basics' } id="basics" class="tab-content">
                <div class="pure-g">
                    <div class="pure-u-1" if={ parent.isSuperAdmin() }>
                        <label for="id">Network</label>
                        <select id="network" name="network" class="pure-input-1">
                            <option each={ parent.networks } value={ id }>{ title }</option>
                        </select>
                        <div if={ parent.errors.network } class="state state-invalid">{ parent.errors.network }</div>
                    </div>

                    <div class="pure-u-1-2">
                        <label for="id">ID</label>
                        <input type="text" id="id" name="id" class="pure-u-23-24" value="{ parent.gateway['$id'] }" />
                        <div if={ parent.errors.id } class="state state-invalid">{ parent.errors.id }</div>
                    </div>

                    <div class="pure-u-1-2">
                        <label for="title">Title</label>
                        <input type="text" id="title" name="title" class="pure-u-1" value={ parent.gateway.title } />
                        <div if={ parent.errors.title } class="state state-invalid">{ parent.errors.title }</div>
                    </div>

                    <div class="pure-u-1">
                        <label for="description">Description</label>
                        <textarea id="description" class="pure-u-1" name="description">{ parent.gateway.description }</textarea>
                        <div if={ parent.errors.description } class="state state-invalid">{ parent.errors.description }</div>
                    </div>
                </div>
            </div>

            <div if={ parent.modal.active == 'contact' } id="contact" class="tab-content">
                <div class="pure-g">
                    <div class="pure-u-1">
                        <label for="contact_email">Email</label>
                        <input type="text" id="contact_email" name="contact_email" class="pure-u-1" value={ parent.gateway.contact_email } />
                        <div if={ parent.errors.contact_email } class="state state-invalid">{ parent.errors.contact_email }</div>
                    </div>

                    <div class="pure-u-1">
                        <label for="contact_phone">Phone Number</label>
                        <input type="text" id="contact_phone" name="contact_phone" class="pure-u-1" value={ parent.gateway.contact_phone } />
                        <div if={ parent.errors.contact_phone } class="state state-invalid">{ parent.errors.contact_phone }</div>
                    </div>
                </div>
            </div>

            <div if={ parent.modal.active == 'social' } id="social" class="tab-content">
                <div class="pure-g">
                    <div class="pure-u-1">
                        <label for="url_home">Home Page</label>
                        <input type="text" id="url_home" name="url_home" class="pure-u-1" value={ parent.gateway.url_home } />
                        <div if={ parent.errors.url_home } class="state state-invalid">{ parent.errors.url_home }</div>
                    </div>

                    <div class="pure-u-1">
                        <label for="url_home">Facebook Page</label>
                        <input type="text" id="url_facebook" name="url_facebook" class="pure-u-1" value={ parent.gateway.url_facebook } />
                        <div if={ parent.errors.url_facebook } class="state state-invalid">{ parent.errors.url_facebook }</div>
                    </div>
                </div>
            </div>

            <div class="actions">
                <button type="button" class="pure-button" onclick={ parent.cancel }>Cancel</button>
                <button type="submit" class="pure-button pure-button-primary" onclick={ parent.save }>Save</button>
            </div>
        </form>
    </modal>

    <h1>Gateways</h1>

    <div class="actions-collection">
        <form class="pure-form">
            <fieldset>
                <button type="button" class="pure-button pure-button-primary" onclick="{ showNewForm }">
                    <span class="oi" data-glyph="file" title="New" aria-hidden="true"></span>
                    New
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
            <tr each={ row, i in gateways } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
                <td if={ isSuperAdmin() }>{ render(row.network) }</td>
                <td><a href="#" onclick={ showEditForm }>{ row['$id'] }</a></td>
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

    <style scoped>
    .tab-content { min-height: 250px; }
    </style>

    var self = this,
        defaultGateway = {
            id: '',
            title: '',
            description: ''
        };

    self.modal = {
        active: 'basics',
        heading: '',
        hidden: true
    };

    RiotControl.on('networks.loaded', function (networks) {
        self.update({ networks });
    });

    RiotControl.on('gateways.loaded', function (gateways) {
        self.update({ gateways });
    });

    RiotControl.on('gateway.loaded', function (gateway) {
        self.errors = {};
        self.gateway = gateway;
        self.modal.heading = gateway.title;
        self.modal.hidden = false;
        self.update();
    });

    RiotControl.on('gateway.error', function (response) {
        self.errors = {};
        response.errors.forEach(function(error) {
            self.errors[error.path[0]] = error.message;
        });
        console.log(self.errors);
        self.update();
    });

    RiotControl.on('gateway.saved', function () {
        self.modal.hidden = true;
        self.update();
    });

    RiotControl.on('currentuser.loaded', function (currentuser) {
        self.update({ currentuser });
    });

    RiotControl.trigger('gateways.load');
    RiotControl.trigger('networks.load');

    showTab(active) {
        return function(e) {
            self.modal.active = active;
            self.update();
            return false;
        }
    }

    isSuperAdmin() {
        return self.currentuser.roles.indexOf('super-admin') > -1;
    }

    getId(e) {
        return $(e.target).closest('tr[data-id]').data('id');
    }

    cancel(e) {
        self.modal.hidden = true;
        self.update();
    }

    save(e) {
        var modal = self.tags.modal,
            data = {
                network: self.isSuperAdmin() ? modal.network.value : self.currentuser.network,
                id: modal.id.value,
                title: modal.title.value,
                description: modal.description.value
            };

        if (modal.original_id.value) {
            RiotControl.trigger('gateway.save', modal.original_id.value, data);
        } else {
            RiotControl.trigger('gateways.create', data);
        }

        return false;
    }

    remove(e) {
        if(confirm('Are you sure?')) {
            RiotControl.trigger('gateway.remove', self.getId(e));
        }
    }

    showEditForm(e) {
        RiotControl.trigger('gateway.load', self.getId(e));
    }

    showNewForm(e) {
        self.gateway = defaultGateway;
        self.modal.heading = 'New Gateway';
        self.modal.hidden = false;
    }
</gateways>
