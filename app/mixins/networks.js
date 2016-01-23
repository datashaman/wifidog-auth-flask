riot.mixin('networks', {
    init: function() {
        RiotControl.on('networks.loaded', function (networks) {
            this.update({ networks: networks });
        }.bind(this));

        RiotControl.trigger('networks.load');
    }
});
