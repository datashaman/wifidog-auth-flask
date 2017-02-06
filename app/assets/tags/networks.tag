<networks>
    <modal heading={ modal.heading } hidden={ modal.hidden } cancelevent="network.cancel" row={ row }>
        <form id="form" class="pure-form pure-form-stacked" onsubmit={ doNothing }>
            <input type="hidden" id="original_id" value={ opts.row['$id'] } />

            <label for="id">ID</label>
            <input type="text" id="id" name="id" class="pure-input-1" value="{ opts.row['$id'] }" />
            <div if={ opts.errors.id } class="state state-invalid">{ opts.errors.id }</div>

            <label for="title">Title</label>
            <input type="text" id="title" name="title" class="pure-input-1" value={ opts.row.title } />
            <div if={ opts.errors.title } class="state state-invalid">{ opts.errors.title }</div>

            <label for="description">Description</label>
            <textarea id="description" class="pure-input-1" name="description">{ opts.row.description }</textarea>
            <div if={ opts.errors.description } class="state state-invalid">{ opts.errors.description }</div>

            <div class="actions">
                <button type="submit" class="pure-button pure-button-primary" onclick={ parent.onOk }>Ok</button>
                <button type="button" class="pure-button" onclick={ parent.triggerEvent('network.cancel') }>Cancel</button>
            </div>
        </form>
    </modal>

    <div class="header">
        <h1>Networks</h1>

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
                    <th>ID</th>
                    <th>Title</th>
                    <th>Description</th>
                    <th>Created At</th>

                    <th class="actions">Actions</th>
                </tr>
            </thead>

            <tbody>
                <tr each={ row, i in rows } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
                    <td data-label="ID"><a href="#" onclick={ onEdit }>{ row['$id'] }</a></td>
                    <td data-label="Title">{ render(row.title) }</td>
                    <td data-label="Description">{ render(row.description) }</td>
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

    $.extend(this, {
        modal: {
            hidden: true
        },
        item: 'network',
        collection: 'networks',
        defaultObject: {
            id: '',
            title: '',
            description: ''
        },
        saveColumns: [
            'id',
            'title',
            'description'
        ]
    });

    this.mixin('crud');
    this.mixin('currentuser');
    this.mixin('events');
    this.mixin('render');
</networks>
