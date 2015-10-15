function Store(item, collection) {
    var self = this;

    if (typeof collection == 'undefined') {
        collection = item + 's';
    }

    var base = '/api/' + collection;

    riot.observable(self);

    self.load_item = function(id) {
        $.getJSON(base + '/' + id, function(data) {
            console.log(item, id, 'loaded', data);
            self.trigger(item + '.loaded', data);
        });
    };

    self.load_collection = function() {
        $.getJSON(base, function(data) {
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

    self.load_currentuser = function() {
        $.getJSON(base, function(data) {
            self.trigger('currentuser.loaded', data);
        });
    };

    self.on('currentuser.load', self.load_currentuser);
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

vouchers.on('voucher.extend', function(id) {
    $.ajax({
        type: 'POST',
        url: '/api/vouchers/' + id + '/extend'
    }).done(function() {
        console.log('voucher', id, 'extended');
        this.load_collection();
    }.bind(this)).fail(function(xhr, errorType, error) {
        console.error('voucher', id, 'error', JSON.parse(xhr.responseText));
        // self.trigger('voucher' + '.error', JSON.parse(xhr.responseText));
    });
});

RiotControl.addStore(currentuser);
RiotControl.addStore(gateways);
RiotControl.addStore(networks);
RiotControl.addStore(users);
RiotControl.addStore(vouchers);
