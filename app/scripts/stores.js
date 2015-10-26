function Store(item, collection) {
    var self = this;

    if (typeof collection == 'undefined') {
        collection = item + 's';
    }

    var base = '/api/' + collection;

    riot.observable(self);

    self.load_item = function(id) {
        $.ajax({
            url: base + '/' + id,
            dataType: 'json'
        }).done(function(data) {
            console.log(item, id, 'loaded', data);
            self.trigger(item + '.loaded', data);
        }).fail(function() {
            console.error(arguments);
        });
    };

    self.load_collection = function() {
        $.getJSON(base)
            .done(function(data) {
                console.log(collection, 'loaded', data);
                self.trigger(collection + '.loaded', data);
            });
    };

    self.on(item + '.load', self.load_item);
    self.on(collection + '.load', self.load_collection);

    self.on(collection + '.create', function(attributes) {
        $.ajax({
            url: base,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(attributes)
        }).done(function(data) {
            console.log(item, 'saved', data);
            self.trigger(item + '.saved', data);
            self.load_collection();
        }).fail(function(xhr, errorType, error) {
            console.error(item, 'error', JSON.parse(xhr.responseText));
            self.trigger(item + '.error', JSON.parse(xhr.responseText));
        });
    });

    self.on(item + '.save', function(id, attributes) {
        console.log(item, id, 'save', attributes);

        $.ajax({
            url: base + '/' + id,
            type: 'PATCH',
            contentType: 'application/json',
            data: JSON.stringify(attributes)
        }).done(function(data) {
            console.log(item, id, 'saved', data);
            self.trigger(item + '.saved', data);
            self.load_collection();
        }).fail(function(xhr, errorType, error) {
            console.error(item, id, 'error', JSON.parse(xhr.responseText));
            self.trigger(item + '.error', JSON.parse(xhr.responseText));
        });
    });

    self.on(item + '.remove', function(id) {
        $.ajax({
            url: base + '/' + id,
            type: 'DELETE',
            success: self.load_collection
        });
    });
}

function CurrentUserStore() {
    var self = this,
        base = '/api/users/current';

    riot.observable(self);

    self.on('currentuser.load', function() {
        $.getJSON(base, function(data) {
            console.log('currentuser', 'loaded', data);
            self.trigger('currentuser.loaded', data);
        });
    });
}

var currentuser = new CurrentUserStore(),
    gateways = new Store('gateway'),
    networks = new Store('network'),
    users = new Store('user'),
    vouchers = new Store('voucher');

gateways.on('gateway.upload', function(id, file) {
    var xhr = new XMLHttpRequest(),
        fd = new FormData(),
        base = '/api/gateways';
    fd.append('file', file);
    xhr.open('post', base + '/' + id + '/logo', true);
    return xhr.send(fd);
});

[ 'expire', 'end', 'extend', 'block', 'unblock', 'archive' ].forEach(function(action) {
    vouchers.on('voucher.' + action, function(id) {
        $.ajax({
            type: 'POST',
            url: '/api/vouchers/' + id + '/' + action
        }).done(function() {
            console.log('voucher', action, id);
            this.load_collection();
        }.bind(this)).fail(function(xhr, errorType, error) {
            console.error('voucher', action, id, 'error', JSON.parse(xhr.responseText));
            // self.trigger('voucher' + '.error', JSON.parse(xhr.responseText));
        });
    });
});

RiotControl.addStore(currentuser);
RiotControl.addStore(gateways);
RiotControl.addStore(networks);
RiotControl.addStore(users);
RiotControl.addStore(vouchers);
