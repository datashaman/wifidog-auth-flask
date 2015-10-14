<networks>
    <modal heading={ modal.heading } hidden={ modal.hidden } dismissable="true" onclose={ cancel }>
        <form class="pure-form pure-form-stacked" onsubmit={ doNothing }>
            <input type="hidden" id="original_id" class="pure-input-1" value={ parent.row['$id'] } />

            <label for="id">ID</label>
            <input type="text" id="id" name="id" class="pure-input-1" value="{ parent.row['$id'] }" />
            <div if={ parent.errors.id } class="state state-invalid">{ parent.errors.id }</div>

            <label for="title">Title</label>
            <input type="text" id="title" name="title" class="pure-input-1" value={ parent.row.title } />
            <div if={ parent.errors.title } class="state state-invalid">{ parent.errors.title }</div>

            <label for="description">Description</label>
            <textarea id="description" class="pure-input-1" name="description">{ parent.row.description }</textarea>
            <div if={ parent.errors.description } class="state state-invalid">{ parent.errors.description }</div>

            <div class="actions">
                <button type="button" class="pure-button" onclick={ parent.cancel }>Cancel</button>
                <button type="submit" class="pure-button pure-button-primary" onclick={ parent.save }>Save</button>
            </div>
        </form>
    </modal>

    <h1>Networks</h1>

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
                <th>ID</th>
                <th>Title</th>
                <th>Description</th>
                <th>Created At</th>

                <th class="actions">Actions</th>
            </tr>
        </thead>

        <tbody>
            <tr each={ row, i in rows } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
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

    this.mixin('render');

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
        saveColumns: [ 'id', 'title', 'description' ]
    });

    this.mixin('crud');
</networks>
