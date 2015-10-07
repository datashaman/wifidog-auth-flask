function NetworkStore() {
    var self = this,
        base = '/api/networks';

    riot.observable(self);

    load_one = function(id) {
        $.getJSON(base + '/' + id, function(data) {
            self.trigger('network.loaded', data);
        });
    };

    load_many = function() {
        $.getJSON(base, function(data) {
            self.trigger('networks.loaded', data.objects);
        });
    };

    self.on('network.load', load_one);
    self.on('networks.load', load_many);

    self.on('networks.create', function(attributes) {
        $.ajax({
            url: base,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(attributes),
            success: function(data) {
                self.trigger('network.saved', data);
                load_many();
            }
        });
    });

    self.on('network.save', function(id, attributes) {
        $.ajax({
            url: base + '/' + id,
            type: 'PATCH',
            contentType: 'application/json',
            data: JSON.stringify(attributes),
            success: function(data) {
                self.trigger('network.saved', data);
                load_many();
            }
        });
    });

    self.on('network.remove', function(id) {
        $.ajax({
            url: base + '/' + id,
            type: 'DELETE',
            success: load_many
        });
    });
}

RiotControl.addStore(new NetworkStore());
