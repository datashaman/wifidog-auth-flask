<networks>
    <modal heading={ modal.heading } hidden={ modal.hidden } dismissable="true" onclose={ cancel }>
        <form class="pure-form pure-form-stacked" onsubmit={ doNothing }>
            <input type="hidden" id="original_id" class="pure-input-1" value={ parent.network['$id'] } />

            <label for="id">ID</label>
            <input type="text" id="id" name="id" class="pure-input-1" value="{ parent.network['$id'] }" />
            <div if={ parent.errors.id } class="state state-invalid">{ parent.errors.id }</div>

            <label for="title">Title</label>
            <input type="text" id="title" name="title" class="pure-input-1" value={ parent.network.title } />
            <div if={ parent.errors.title } class="state state-invalid">{ parent.errors.title }</div>

            <label for="description">Description</label>
            <textarea id="description" class="pure-input-1" name="description">{ parent.network.description }</textarea>
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

    var self = this,
        defaultNetwork = {
            id: '',
            title: '',
            description: ''
        };

    self.mixin('render');

    self.rows = [];

    self.modal = {
        heading: '',
        hidden: true
    };

    RiotControl.on('networks.loaded', function (networks) {
        self.rows = networks;
        self.update();
    });

    RiotControl.on('network.loaded', function (network) {
        self.network = network;
        self.modal.heading = network.title;
        self.modal.hidden = false;
        self.update();
    });

    RiotControl.on('network.error', function (response) {
        self.errors = {};
        response.errors.forEach(function(error) {
            self.errors[error.path[0]] = error.message;
        });
        self.update();
    });

    RiotControl.on('network.saved', function () {
        self.modal.hidden = true;
        self.update();
    });

    RiotControl.trigger('networks.load');

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
                id: modal.id.value,
                title: modal.title.value,
                description: modal.description.value
            };

        if (modal.original_id.value) {
            RiotControl.trigger('network.save', modal.original_id.value, data);
        } else {
            RiotControl.trigger('networks.create', data);
        }

        return false;
    }

    remove(e) {
        if(confirm('Are you sure?')) {
            RiotControl.trigger('network.remove', self.getId(e));
        }
    }

    showEditForm(e) {
        RiotControl.trigger('network.load', self.getId(e));
    }

    showNewForm(e) {
        self.network = defaultNetwork;
        self.modal.heading = 'New Network';
        self.modal.hidden = false;
    }
</networks>
