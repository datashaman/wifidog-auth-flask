function UserStore() {
    var self = this;

    riot.observable(self);

    triggerUpdate = function() {
        $.getJSON('/users/', function(data) {
            self.trigger('users.updated', data.users);
        });
    };

    self.on('users.create', function(id, password) {
        $.ajax({
            url: '/users/',
            type: 'POST',
            data: {
                id,
                password
            },
            success: triggerUpdate
        });
    });

    self.on('user.remove', function(id) {
        $.ajax({
            url: '/users/' + id,
            type: 'DELETE',
            success: triggerUpdate
        });
    });

    self.on('users.remove', function() {
        $.ajax({
            url: '/users/',
            type: 'DELETE',
            success: triggerUpdate
        });
    });
}

RiotControl.addStore(new UserStore());
