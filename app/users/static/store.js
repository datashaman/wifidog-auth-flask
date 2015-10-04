function UserStore() {
    var self = this,
        base = '/api/users';

    riot.observable(self);

    triggerUpdate = function() {
        $.getJSON(base, function(data) {
            self.trigger('users.updated', data.objects);
        });
    };

    self.on('users.create', function(email, password) {
        $.ajax({
            url: base,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                email,
                password
            }),
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
