function UserStore() {
    var self = this,
        base = '/api/users';

    riot.observable(self);

    triggerUpdate = function() {
        $.getJSON(base, function(data) {
            self.trigger('users.loaded', data);
        });
    };

    self.on('users.load', triggerUpdate);

    self.on('users.create', function(attributes) {
        $.ajax({
            url: base,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(attributes),
            success: triggerUpdate
        });
    });

    self.on('user.remove', function(id) {
        $.ajax({
            url: base + '/' + id,
            type: 'DELETE',
            success: triggerUpdate
        });
    });

    self.on('users.remove', function() {
        $.ajax({
            url: base,
            type: 'DELETE',
            success: triggerUpdate
        });
    });
}

RiotControl.addStore(new UserStore());
