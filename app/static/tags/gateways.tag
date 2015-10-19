<gateways>
    <modal heading={ modal.heading } hidden={ modal.hidden } dismissable="true" onclose={ cancel }>
        <form class="pure-form pure-form-stacked" onsubmit={ doNothing }>
            <input type="hidden" id="original_id" class="pure-input-1" value={ parent.row['$id'] } />

            <div class="pure-menu pure-menu-horizontal">
                <ul class="pure-menu-list">
                    <li class="pure-menu-item { 'pure-menu-selected': parent.modal.active == 'basics' }"><a href="#" onclick={ parent.showTab('basics') } class="pure-menu-link">Basics</a></li>
                    <li class="pure-menu-item { 'pure-menu-selected': parent.modal.active == 'contact' }"><a href="#" onclick={ parent.showTab('contact') } class="pure-menu-link">Contact</a></li>
                    <li class="pure-menu-item { 'pure-menu-selected': parent.modal.active == 'social' }"><a href="#" onclick={ parent.showTab('social') } class="pure-menu-link">Social</a></li>
                    <li class="pure-menu-item { 'pure-menu-selected': parent.modal.active == 'logo' }"><a href="#" onclick={ parent.showTab('logo') } class="pure-menu-link">Logo</a></li>
                </ul>
            </div>

            <div if={ parent.modal.active == 'basics' } id="tab-basics" class="tab-content">
                <div class="pure-g">
                    <div class="pure-u-1" if={ parent.hasRole('super-admin') }>
                        <label for="id">Network</label>
                        <select id="network" name="network" class="pure-input-1">
                            <option each={ parent.networks } value={ id }>{ title }</option>
                        </select>
                        <div if={ parent.errors.network } class="state state-invalid">{ parent.errors.network }</div>
                    </div>

                    <div class="pure-u-1-2">
                        <label for="id">ID</label>
                        <input type="text" id="id" name="id" class="pure-u-23-24" value="{ parent.row['$id'] }" />
                        <div if={ parent.errors.id } class="state state-invalid">{ parent.errors.id }</div>
                    </div>

                    <div class="pure-u-1-2">
                        <label for="title">Title</label>
                        <input type="text" id="title" name="title" class="pure-u-1" value={ parent.row.title } />
                        <div if={ parent.errors.title } class="state state-invalid">{ parent.errors.title }</div>
                    </div>

                    <div class="pure-u-1">
                        <label for="description">Description</label>
                        <textarea id="description" class="pure-u-1" name="description">{ parent.row.description }</textarea>
                        <div if={ parent.errors.description } class="state state-invalid">{ parent.errors.description }</div>
                    </div>
                </div>
            </div>

            <div if={ parent.modal.active == 'contact' } id="tab-contact" class="tab-content">
                <div class="pure-g">
                    <div class="pure-u-1">
                        <label for="contact_email">Email</label>
                        <input type="text" id="contact_email" name="contact_email" class="pure-u-1" value={ parent.row.contact_email } />
                        <div if={ parent.errors.contact_email } class="state state-invalid">{ parent.errors.contact_email }</div>
                    </div>

                    <div class="pure-u-1">
                        <label for="contact_phone">Phone Number</label>
                        <input type="text" id="contact_phone" name="contact_phone" class="pure-u-1" value={ parent.row.contact_phone } />
                        <div if={ parent.errors.contact_phone } class="state state-invalid">{ parent.errors.contact_phone }</div>
                    </div>
                </div>
            </div>

            <div if={ parent.modal.active == 'social' } id="tab-social" class="tab-content">
                <div class="pure-g">
                    <div class="pure-u-1">
                        <label for="url_home">Home Page</label>
                        <input type="text" id="url_home" name="url_home" class="pure-u-1" value={ parent.row.url_home } />
                        <div if={ parent.errors.url_home } class="state state-invalid">{ parent.errors.url_home }</div>
                    </div>

                    <div class="pure-u-1">
                        <label for="url_home">Facebook Page</label>
                        <input type="text" id="url_facebook" name="url_facebook" class="pure-u-1" value={ parent.row.url_facebook } />
                        <div if={ parent.errors.url_facebook } class="state state-invalid">{ parent.errors.url_facebook }</div>
                    </div>
                </div>
            </div>

            <div if={ parent.modal.active == 'logo' } id="tab-logo" class="tab-content">
                <img if={ parent.row.logo } src="/static/logos/{ parent.row.logo }" />

                <div class="pure-g">
                    <div class="pure-u-1">
                        <label for="url_home">File Upload</label>
                        <input type="file" id="logo" name="logo" class="pure-u-1" />
                        <div if={ parent.errors.logo } class="state state-invalid">{ parent.errors.logo }</div>
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

    <table if={ rows.length } width="100%" cellspacing="0" class="pure-table pure-table-horizontal">
        <thead>
            <tr>
                <th if={ hasRole('super-admin') }>Network</th>
                <th>ID</th>
                <th>Title</th>
                <th>Created At</th>

                <th class="actions">Actions</th>
            </tr>
        </thead>

        <tbody>
            <tr each={ row, i in rows } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
                <td if={ hasRole('super-admin') }>{ render(row.network) }</td>
                <td><a href="#" onclick={ showEditForm }>{ row['$id'] }</a></td>
                <td>{ render(row.title) }</td>
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

    showTab(active) {
        return function(e) {
            this.modal.active = active;
            this.update();
            return e;
        }.bind(this);
    }

    this.mixin('render');
    this.mixin('currentuser');

    $.extend(this, {
        item: 'gateway',
        collection: 'gateways',
        defaultObject: {
            id: '',
            title: '',
            description: ''
        },
        modal: {
            active: 'basics',
            heading: '',
            hidden: true
        },
        saveColumns: [
            'id',
            'title',
            'description',
            'contact_email',
            'contact_phone',
            'url_home',
            'url_facebook'
        ],
        beforeSave: function(data, modal) {
            data.network = this.hasRole('super-admin') ? modal.network.value : this.currentuser.network;
            console.log(data);
        }
    });

    this.mixin('crud');

    RiotControl.trigger('networks.loaded', function (networks) {
        this.update({ networks: networks });
    }.bind(this));

    RiotControl.trigger('networks.load');
</gateways>
