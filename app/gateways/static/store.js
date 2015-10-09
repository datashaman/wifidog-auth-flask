function GatewayStore() {
    var self = this,
        base = '/api/gateways';

    riot.observable(self);

    triggerUpdate = function() {
        $.getJSON(base, function(data) {
            self.trigger('gateways.updated', data);
        });
    };

    self.on('gateways.load', triggerUpdate);

    self.on('gateways.create', function(id, title, description) {
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

    self.on('gateway.remove', function(id) {
        $.ajax({
            url: base + '/' + id,
            type: 'DELETE',
            success: triggerUpdate
        });
    });
}

RiotControl.addStore(new GatewayStore());
