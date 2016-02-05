riot.mixin('currencies', {
    init: function() {
        RiotControl.on('currencies.loaded', function (currencies) {
            this.update({ currencies: currencies });
        }.bind(this));

        RiotControl.trigger('currencies.load');
    }
});
