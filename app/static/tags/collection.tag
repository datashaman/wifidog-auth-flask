<collection>
    <div class="header">
        <h1>{ opts.title }</h1>

        <div class="actions-collection">
            <form class="pure-form">
                <fieldset>
                    <button type="button" class="pure-button pure-button-primary" onclick={ opts.onNew }>
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
                    <td if={ hasRole('super-admin') }>{ render(row.network) }</td>
                    <td><a href="#" onclick={ opts.onEdit }>{ row['$id'] }</a></td>
                    <td>{ render(row.title) }</td>
                    <td>{ render(row.created_at) }</td>

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
            title: ''
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
        }
    });

    this.mixin('crud');
    this.mixin('currentuser');
    this.mixin('networks');
    this.mixin('render');

    showTab(active) {
        return function(e) {
            this.modal.active = active;
            this.update();
            return e;
        }.bind(this);
    }
</collection>
