function VoucherStore() {
    var self = this;

    riot.observable(self);

    triggerUpdate = function() {
        $.getJSON('/vouchers/', function(data) {
            self.trigger('vouchers.updated', data.vouchers);
        });
    };

    self.on('vouchers.create', function(minutes) {
        $.ajax({
            url: '/vouchers/',
            type: 'POST',
            data: {
                minutes
            },
            success: triggerUpdate
        });
    });

    self.on('voucher.remove', function(id) {
        $.ajax({
            url: '/vouchers/' + id,
            type: 'DELETE',
            success: triggerUpdate
        });
    });

    self.on('vouchers.remove', function() {
        $.ajax({
            url: '/vouchers/',
            type: 'DELETE',
            success: triggerUpdate
        });
    });
}

RiotControl.addStore(new VoucherStore());
