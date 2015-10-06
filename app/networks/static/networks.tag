<networks>
    <h1>Networks</h1>

    <div class="actions-collection">
        <form class="pure-form" onsubmit={ doNothing }>
            <fieldset>
                <button type="button" class="pure-button pure-button-primary" onclick={ showNewForm }>
                    <span class="oi" data-glyph="file" title="New" aria-hidden="true"></span>
                    New
                </button>
            </fieldset>
        </form>
    </div>

    <table if={ networks.length } width="100%" cellspacing="0" class="pure-table pure-table-horizontal">
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
            <tr each={ row, i in networks } data-id={ row.id } class={ pure-table-odd: i % 2 }>
                <td><a href="/networks/{ row.id }">{ row.id }</a></td>
                <td>{ row.title }</td>
                <td>{ row.description }</td>
                <td>{ renderDateTime(row.created_at) }</td>

                <td class="actions actions-row">
                    <button class="pure-button" onclick={ remove }>
                        <span class="oi" data-glyph="x" title="Remove" aria-hidden="true"></span>
                        Remove
                    </button>
                </td>
            </tr>
        </tbody>
    </table>

    <script>
    var self = this;

    RiotControl.on('networks.updated', function (networks) {
        self.networks = networks;
        self.update();
    });

    RiotControl.trigger('networks.load');

    renderDateTime(dt) {
        if (dt) {
            dt = new Date(dt);
            return dt.toLocaleString();
        }
    }

    getId(e) {
        return $(e.target).closest('tr[data-id]').data('id');
    }

    create(e) {
        RiotControl.trigger('networks.create', self.id.value, self.title.value, self.description.value);
        return false;
    }

    remove(e) {
        if(confirm('Are you sure?')) {
            RiotControl.trigger('network.remove', self.getId(e));
        }
    }

    doNothing(e) {
        return false;
    }

    showNewForm(e) {
        self.formVisible = true;
        self.update();
    }
    </script>
</networks>
