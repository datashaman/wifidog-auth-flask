function Store(item, collection) {
    var self = this;

    if (typeof collection == 'undefined') {
        collection = item + 's';
    }

    var base = '/api/' + collection;

    riot.observable(self);

    load_item = function(id) {
        $.getJSON(base + '/' + id, function(data) {
            self.trigger(item + '.loaded', data);
        });
    };

    load_collection = function() {
        $.getJSON(base, function(data) {
            self.trigger(collection + '.loaded', data);
        });
    };

    self.on(item + '.load', load_item);
    self.on(collection + '.load', load_collection);

    self.on(collection + '.create', function(attributes) {
        $.ajax({
            url: base,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(attributes)
        }).done(function(data) {
            self.trigger(item + '.saved', data);
            load_collection();
        }).fail(function(xhr, errorType, error) {
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
            self.trigger(item + '.saved', data);
            load_collection();
        }).fail(function(xhr, errorType, error) {
            self.trigger(item + '.error', JSON.parse(xhr.responseText));
        });
    });

    self.on(item + '.remove', function(id) {
        $.ajax({
            url: base + '/' + id,
            type: 'DELETE',
            success: load_collection
        });
    });
}

function render(attribute) {
    switch(typeof attribute) {
        case 'object':
            if (typeof attribute.$date != 'undefined') {
                var date = new Date(attribute.$date);
                return date.toLocaleString();
            }

            if (typeof attribute.$ref != 'undefined') {
                return attribute.$ref.replace(/^.*\//, '');
            }
            break;
        default:
            return attribute;
    }
}
