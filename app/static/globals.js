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
        default:
            return attribute;
    }
}

/**
 * From https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API/Using_the_Notifications_API
 */
function setupNotifications() {
  if ("Notification" in window) {
    switch (Notification.permission) {
    case 'granted':
        console.log('Notification permission previously granted');
        break;
    case 'denied':
        console.log('Notification permission previously denied');;
        break;
    default:
        Notification.requestPermission(function (permission) {
            switch (permission) {
            case 'granted':
                console.log('Notification permission granted');
                var notification = new Notification('Notifications here will be used to keep you updated');
                break;
            default:
                console.log('Notification permission ' + permission);
            }
        });
    }
  } else {
    console.log('Notification API not supported');
  }
}
