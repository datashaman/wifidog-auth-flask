function CurrentUserStore() {
    var self = this,
        base = '/api/users/current';

    riot.observable(self);

    triggerUpdate = function() {
        $.getJSON(base, function(data) {
            self.trigger('currentuser.loaded', data);
        });
    };

    self.on('currentuser.load', triggerUpdate);
}

RiotControl.addStore(new CurrentUserStore());
