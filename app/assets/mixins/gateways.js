riot.mixin('gateways', {
    init: function() {
        RiotControl.on('gateways.loaded', function (gateways) {
            this.update({ gateways: gateways });
        }.bind(this));

        RiotControl.trigger('gateways.load');
    }
});
