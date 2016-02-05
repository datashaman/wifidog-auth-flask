<currencies>
    <modal heading={ modal.heading } hidden={ modal.hidden } cancelevent="currency.cancel" row={ row }>
        <form id="form" class="pure-form pure-form-stacked" onsubmit={ doNothing }>
            <input type="hidden" id="original_id" value={ opts.row['$id'] } />

            <label for="id">ID</label>
            <input type="text" id="id" name="id" class="pure-input-1" value="{ opts.row['$id'] }" />
            <div if={ opts.errors.id } class="state state-invalid">{ opts.errors.id }</div>

            <label for="title">Title</label>
            <input type="text" id="title" name="title" class="pure-input-1" value={ opts.row.title } />
            <div if={ opts.errors.title } class="state state-invalid">{ opts.errors.title }</div>

            <label for="prefix">Prefix</label>
            <input type="text" id="prefix" name="prefix" class="pure-input-1" value={ opts.row.prefix } />
            <div if={ opts.errors.prefix } class="state state-invalid">{ opts.errors.prefix }</div>

            <label for="suffix">Suffix</label>
            <input type="text" id="suffix" name="suffix" class="pure-input-1" value={ opts.row.suffix } />
            <div if={ opts.errors.suffix } class="state state-invalid">{ opts.errors.suffix }</div>

            <div class="actions">
                <button type="submit" class="pure-button pure-button-primary" onclick={ parent.onOk }>Ok</button>
                <button type="button" class="pure-button" onclick={ parent.triggerEvent('currency.cancel') }>Cancel</button>
            </div>
        </form>
    </modal>

    <div class="header">
        <h1>currencies</h1>

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
                    <th>Prefix</th>
                    <th>Suffix</th>
                    <th class="actions">Actions</th>
                </tr>
            </thead>

            <tbody>
                <tr each={ row, i in rows } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
                    <td data-label="ID"><a href="#" onclick={ onEdit }>{ row['$id'] }</a></td>
                    <td data-label="Title">{ render(row.title) }</td>
                    <td data-label="Prefix">{ render(row.prefix) }</td>
                    <td data-label="Suffix">{ render(row.suffix) }</td>

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
        item: 'currency',
        collection: 'currencies',
        defaultObject: {
            id: '',
            title: '',
            prefix: '',
            suffix: ''
        },
        saveColumns: [
            'id',
            'title',
            'prefix',
            'suffix'
        ]
    });

    this.mixin('crud');
    this.mixin('currentuser');
    this.mixin('events');
    this.mixin('render');
</currencies>
