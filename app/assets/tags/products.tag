<products>
    <modal heading={ modal.heading } hidden={ modal.hidden } cancelevent="product.cancel" row={ row } errors={ errors }>
        <form id="form" class="pure-form pure-form-stacked" onsubmit={ doNothing }>
            <input type="hidden" id="original_id" value={ opts.row['$id'] } />

            <div if={ parent.hasRole('super-admin') }>
                <label for="network">Network</label>
                <select id="network" name="network" class="pure-input-1">
                    <option each={ parent.networks } value={ id } selected={ id == network_id }>{ title }</option>
                </select>
                <div if={ opt.errors.network } class="state state-invalid">{ opt.errors.network }</div>
            </div>

            <div if={ parent.hasRole('super-admin') || parent.hasRole('network-admin') }>
                <label for="gateway">Gateway</label>
                <select id="gateway" name="gateway" class="pure-input-1">
                    <option each={ parent.gateways } value={ id } selected={ id == gateway_id }>{ title }</option>
                </select>
                <div if={ opt.errors.gateway } class="state state-invalid">{ opt.errors.gateway }</div>
            </div>

            <label for="code">Code</label>
            <input type="text" id="code" name="code" class="pure-input-1" value={ opts.row.code } />
            <div if={ opts.errors.code } class="state state-invalid">{ opts.errors.code }</div>

            <label for="title">Title</label>
            <input type="text" id="title" name="title" class="pure-input-1" value={ opts.row.title } />
            <div if={ opts.errors.title } class="state state-invalid">{ opts.errors.title }</div>

            <label for="description">Description</label>
            <textarea id="description" class="pure-input-1" name="description">{ opts.row.description }</textarea>
            <div if={ opts.errors.description } class="state state-invalid">{ opts.errors.description }</div>

            <label for="currency">Currency</label>
            <select id="currency" name="currency" class="pure-input-1">
                <option each={ parent.currencies } value={ id } selected={ id == currency_id }>{ title }</option>
            </select>
            <div if={ opt.errors.currency } class="state state-invalid">{ opt.errors.currency }</div>

            <div class="actions">
                <button type="submit" class="pure-button pure-button-primary" onclick={ parent.onOk }>Ok</button>
                <button type="button" class="pure-button" onclick={ parent.triggerEvent('product.cancel') }>Cancel</button>
            </div>
        </form>
    </modal>

    <div class="header">
        <h1>Products</h1>

        <div class="actions-collection">
            <button type="button" class="pure-button pure-button-primary" onclick={ onNew }>
                <span class="oi" data-glyph="file" title="New" aria-hidden="true"></span>
                New
            </button>
        </div>
    </div>

    <div class="content">
        <table if={ rows.length } width="100%" cellspacing="0" class="pure-table pure-table-horizontal">
            <thead>
                <tr>
                    <th if={ hasRole('super-admin') }>Network</th>
                    <th if={ hasRole('super-admin') || hasRole('network-admin') }>Gateway</th>
                    <th>Code</th>
                    <th>Title</th>
                    <th class="actions">Actions</th>
                </tr>
            </thead>

            <tbody>
                <tr each={ row, i in rows } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
                    <td if={ hasRole('super-admin') } data-label="Network">{ render(row.network) }</td>
                    <td if={ hasRole('super-admin') || hasRole('network-admin') } data-label="Gateway">{ render(row.gateway) }</td>
                    <td class="code" data-label="Code"><a href="#" onclick={ onEdit }>{ row.code }</a></td>
                    <td class="title" data-label="Title">{ row.title ? row.title : '-' }</td>

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

    $.extend(this, {
        modal: {
            hidden: true
        },
        item: 'product',
        collection: 'products',
        defaultObject: {
            code: '',
            title: '',
            description: ''
        },
        saveColumns: [
            'network',
            'gateway',
            'code',
            'title',
            'description',
            'currency'
        ]
    });

    this.mixin('crud');
    this.mixin('currentuser');
    this.mixin('events');
    this.mixin('networks');
    this.mixin('gateways');
    this.mixin('currencies');
    this.mixin('render');
</products>
