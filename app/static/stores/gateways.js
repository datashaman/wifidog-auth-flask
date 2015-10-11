var store = new Store('gateway');

store.on('gateway.upload', function(id, file) {
    var xhr = new XMLHttpRequest(),
        fd = new FormData(),
        base = '/api/gateways';
    fd.append('file', file);
    xhr.open('post', base + '/' + id + '/logo', true);
    return xhr.send(fd);
});

RiotControl.addStore(store);
