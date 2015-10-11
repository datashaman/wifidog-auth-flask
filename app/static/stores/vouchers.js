var store = new Store('voucher');

store.on('voucher.toggle', function(id) {
    $.ajax({
        type: 'POST',
        url: '/api/vouchers/' + id + '/toggle'
    }).done(function() {
        RiotControl.trigger('vouchers.load');
    });
});

RiotControl.addStore(store);
