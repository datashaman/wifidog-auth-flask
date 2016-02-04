<categories>
    <div class="header">
        <h1>Categories</h1>

        <div class="actions-collection">
            <a href="/new-voucher" class="pure-button pure-button-primary">
                <span class="oi" data-glyph="file" title="New Category" aria-hidden="true"></span>
                New Category
            </a>
        </div>
    </div>

    <div class="content">
        <table if={ categories.length } id="categories" width="100%" cellspacing="0" class="pure-table pure-table-horizontal">
            <thead>
                <tr>
                    <th>Code</th>
                    <th>Title</th>
                    <th class="actions">Actions</th>
                </tr>
            </thead>

            <tbody>
                <tr each={ row, i in categories } data-id={ row['$id'] } class={ pure-table-odd: i % 2 }>
                    <td class="code" data-label="Code">{ row.code }</td>
                    <td class="title" data-label="Title">{ row.title ? row.title : '-' }</td>

                    <td class="actions actions-row">
                        <button class="pure-button" each={ action, defn in row.available_actions } value={ action } title={ action } onclick={ handleAction }>
                            <span if={ defn.icon } class="oi" data-glyph={ defn.icon } aria-hidden="true"></span>
                            { action }
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    var self = this;

    self.mixin('render');
    self.mixin('currentuser');

    self.categories = [];

    self.statusIcons = {
        new: 'file',
        active: 'bolt',
        ended: 'flag',
        expired: 'circle-x',
        archived: 'trash',
        blocked: 'thumb-down'
    };

    RiotControl.on('categories.loaded', function (categories) {
        self.categories = categories;
        self.update();
    });

    RiotControl.trigger('categories.load');

    handleAction(e) {
        var action = $(e.target).val(),
            id = self.getId(e);

        console.log('category', action, id);

        switch(action) {
        case 'delete':
        case 'archive':
            if(confirm('Are you sure?')) {
                RiotControl.trigger('category.' + action, id);
            }
            break;
        default:
            RiotControl.trigger('category.' + action, id);
        }
    }

    getId(e) {
        return $(e.target).closest('tr[data-id]').data('id');
    }

    create(e) {
        RiotControl.trigger('categories.create', {
            parent_id: self.parent_id.value,
            network: self.hasRole('super-admin') ? self.network.value : self.currentuser.network,
            gateway: self.hasRole('super-admin') || self.hasRole('network-admin') ? self.gateway.value : self.currentuser.gateway,
            code: self.code.value,
            title: self.title.value,
            description: self.description.value
        });
        return false;
    }
</categories>
