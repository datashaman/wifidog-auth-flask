function NetworkStore() {
    var self = this,
        base = '/api/networks';

    riot.observable(self);

    triggerUpdate = function() {
        $.getJSON(base, function(data) {
            self.trigger('networks.updated', data.objects);
        });
    };

    self.on('networks.load', triggerUpdate);

    self.on('networks.create', function(id, title, description) {
        $.ajax({
            url: base,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                id,
                title,
                description
            }),
            success: triggerUpdate
        });
    });

    self.on('network.remove', function(id) {
        $.ajax({
            url: base + '/' + id,
            type: 'DELETE',
            success: triggerUpdate
        });
    });
}

RiotControl.addStore(new NetworkStore());
