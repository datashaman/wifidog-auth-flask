riot.mixin('crud', {
    init: function() {
        RiotControl.on(this.collection + '.loaded', function (rows) {
            this.rows = rows;
            this.update();
        }.bind(this));

        RiotControl.on(this.item + '.loaded', function (row) {
            this.row = row;
            this.modal.heading = row.title;
            this.modal.hidden = false;
            this.update();
        }.bind(this));

        RiotControl.on(this.item + '.error', function (response) {
            this.errors = {};
            response.errors.forEach(function(error) {
                this.errors[error.path[0]] = error.message;
            });
            this.update();
        }.bind(this));

        RiotControl.on(this.item + '.saved', function () {
            this.modal.hidden = true;
            this.update();
        }.bind(this));

        RiotControl.trigger(this.collection + '.load');
    },

    getId: function(e) {
        return $(e.target).closest('tr[data-id]').data('id');
    },

    cancel: function(e) {
        this.modal.hidden = true;
        this.update();
    },

    save: function(e) {
        var modal = this.tags.modal,
            data = {};

        this.saveColumns.forEach(function(column) {
            data[column] = modal[column].value;
        });

        if (this.beforeSave !== undefined) {
            this.beforeSave(data, modal);
        }

        if (modal.original_id.value) {
            RiotControl.trigger(this.item + '.save', modal.original_id.value, data);
        } else {
            RiotControl.trigger(this.collection + '.create', data);
        }

        return false;
    },

    remove: function(e) {
        if(confirm('Are you sure?')) {
            RiotControl.trigger(this.item + '.remove', this.getId(e));
        }
    },

    showEditForm: function(e) {
        RiotControl.trigger(this.item + '.load', this.getId(e));
    },

    showNewForm: function(e) {
        this.row = this.defaultObject;
        this.modal.heading = 'New ' + this.item;
        this.modal.hidden = false;
    }
});
