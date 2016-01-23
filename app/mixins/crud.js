riot.mixin('crud', {
    init: function() {
        RiotControl.on(this.collection + '.loaded', function (rows) {
            this.update({ rows: rows });
        }.bind(this));

        RiotControl.on(this.item + '.loaded', function (row) {
            this.row = row;
            this.modal.heading = row.title;
            this.modal.hidden = false;
            this.update();
        }.bind(this));

        RiotControl.on(this.item + '.error', function (response) {
            var errors = {};
            response.errors.forEach(function(error) {
                errors[error.path[0]] = error.message;
            });
            this.update({ errors: errors });
        }.bind(this));

        RiotControl.on(this.item + '.saved', function () {
            this.modal.hidden = true;
            this.update();
        }.bind(this));

        RiotControl.on(this.item + '.cancel', function(e) {
            var self = this;
            $(this.tags.modal.form).find('[name]').each(function() {
                var value = self.row[$(this).attr('name')];

                if (typeof value == 'object' && value !== null) {
                    if (typeof value['$ref'] != 'undefined') {
                        var result = /[^\/]*$/.exec(value['$ref']);
                        value = result[0];
                    }
                }

                $(this).val(value);
            });
            self.modal.hidden = true;
            self.update();
        }.bind(this)),

        RiotControl.trigger(this.collection + '.load');
    },

    getId: function(e) {
        return $(e.target).closest('tr[data-id]').data('id');
    },

    onOk: function(e) {
        var modal = this.tags.modal,
            data = {};

        this.saveColumns.forEach(function(column) {
            data[column] = $(modal[column]).val();
        });

        if(this.beforeSave !== undefined) {
            this.beforeSave(data, modal);
        }

        if (modal.original_id.value) {
            RiotControl.trigger(this.item + '.save', modal.original_id.value, data);
        } else {
            RiotControl.trigger(this.collection + '.create', data);
        }

        return false;
    },

    onRemove: function(e) {
        var id = this.getId(e);
        console.log('onRemove', id);
        if(confirm('Are you sure?')) {
            RiotControl.trigger(this.item + '.remove', id);
        }
    },

    onEdit: function(e) {
        var id = this.getId(e);
        console.log('onEdit', id);
        RiotControl.trigger(this.item + '.load', id);
    },

    onNew: function(e) {
        console.log('onNew');
        this.row = this.defaultObject;
        this.modal.heading = 'New ' + this.item;
        this.modal.hidden = false;
    }
});
