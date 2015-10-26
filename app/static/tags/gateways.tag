<gateways>
    <modal hidden={ modal.hidden } heading={ modal.heading } cancelevent="gateway.cancel" row={ row } errors={ errors }>
        <form id="form" class="pure-form pure-form-stacked" onsubmit={ doNothing }>
            <input type="hidden" id="original_id" class="pure-input-1" value={ opts.row['$id'] } />

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
                            <option each={ parent.networks } value={ id } selected={ id == network_id }>{ title }</option>
                        </select>
                        <div if={ opt.errors.network } class="state state-invalid">{ opt.errors.network }</div>
                    </div>

                    <div class="pure-u-1-2">
                        <label for="id">ID</label>
                        <input type="text" id="id" name="id" class="pure-u-23-24" value={ opts.row['$id'] } />
                        <div if={ opt.errors.id } class="state state-invalid">{ opt.errors.id }</div>
                    </div>

                    <div class="pure-u-1-2">
                        <label for="title">Title</label>
                        <input type="text" id="title" name="title" class="pure-u-1" value={ opts.row.title } />
                        <div if={ opt.errors.title } class="state state-invalid">{ opt.errors.title }</div>
                    </div>

                    <div class="pure-u-1">
                        <label for="description">Description</label>
                        <textarea id="description" class="pure-u-1" name="description">{ opts.row.description }</textarea>
                        <div if={ opt.errors.description } class="state state-invalid">{ opt.errors.description }</div>
                    </div>
                </div>
            </div>

            <div if={ parent.modal.active == 'contact' } id="tab-contact" class="tab-content">
                <div class="pure-g">
                    <div class="pure-u-1">
                        <label for="contact_email">Email</label>
                        <input type="text" id="contact_email" name="contact_email" class="pure-u-1" value={ opts.row.contact_email } />
                        <div if={ opt.errors.contact_email } class="state state-invalid">{ opt.errors.contact_email }</div>
                    </div>

                    <div class="pure-u-1">
                        <label for="contact_phone">Phone Number</label>
                        <input type="text" id="contact_phone" name="contact_phone" class="pure-u-1" value={ opts.row.contact_phone } />
                        <div if={ opt.errors.contact_phone } class="state state-invalid">{ opt.errors.contact_phone }</div>
                    </div>
                </div>
            </div>

            <div if={ parent.modal.active == 'social' } id="tab-social" class="tab-content">
                <div class="pure-g">
                    <div class="pure-u-1">
                        <label for="url_home">Home Page</label>
                        <input type="text" id="url_home" name="url_home" class="pure-u-1" value={ opts.row.url_home } />
                        <div if={ opt.errors.url_home } class="state state-invalid">{ opt.errors.url_home }</div>
                    </div>

                    <div class="pure-u-1">
                        <label for="url_home">Facebook Page</label>
                        <input type="text" id="url_facebook" name="url_facebook" class="pure-u-1" value={ opts.row.url_facebook } />
                        <div if={ opt.errors.url_facebook } class="state state-invalid">{ opt.errors.url_facebook }</div>
                    </div>
                </div>
            </div>

            <div if={ parent.modal.active == 'logo' } id="tab-logo" class="tab-content">
                <img if={ opts.row.logo } src="/static/logos/{ opts.row.logo }" />

                <div class="pure-g">
                    <div class="pure-u-1">
                        <label for="url_home">File Upload</label>
                        <input type="file" id="logo" name="logo" class="pure-u-1" />
                        <div if={ opt.errors.logo } class="state state-invalid">{ opt.errors.logo }</div>
                    </div>
                </div>
            </div>

            <div class="actions">
                <button type="submit" class="pure-button pure-button-primary" onclick={ parent.onOk }>Ok</button>
                <button type="button" class="pure-button" onclick={ parent.triggerEvent('gateway.cancel') }>Cancel</button>
            </div>
        </form>
    </modal>

    <div class="header">
        <h1>Gateways</h1>

        <div class="actions-collection">
            <form class="pure-form">
                <fieldset>
                    <button type="button" class="pure-button pure-button-primary" onclick={ onNew }>
                        <span class="oi" data-glyph="file" title="New" aria-hidden="true"></span>
                        New
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
                    <th>ID</th>
                    <th>Title</th>
                    <th>Created At</th>

                    <th class="actions">Actions</th>
                </tr>
            </thead>

            <tbody>
                <tr each={ row, i in rows } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
                    <td if={ hasRole('super-admin') } data-label="Network">{ render(row.network) }</td>
                    <td data-label="ID"><a href="#" onclick={ onEdit }>{ row['$id'] }</a></td>
                    <td data-label="Title">{ render(row.title) }</td>
                    <td data-label="Created At">{ render(row.created_at) }</td>

                    <td class="actions actions-row">
                        <button class="pure-button" onclick={ onRemove }>
                            <span class="oi" data-glyph="x" title="Remove" aria-hidden="true"></span>
                            Remove
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <style scoped>
    .tab-content { min-height: 250px; }
    </style>

    $.extend(this, {
        item: 'gateway',
        collection: 'gateways',
        defaultObject: {
            id: '',
            title: '',
            description: ''
        },
        modal: {
            hidden: true,
            heading: '',
            active: 'basics'
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
    });

    this.mixin('crud');
    this.mixin('currentuser');
    this.mixin('events');
    this.mixin('networks');
    this.mixin('render');

    beforeSave(data, modal) {
        data.network = this.hasRole('super-admin') ? modal.network.value : this.currentuser.network;
    }

    showTab(active) {
        return function(e) {
            this.modal.active = active;
            this.update();
        }.bind(this);
    }
</gateways>
