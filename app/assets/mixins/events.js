riot.mixin('events', {
    triggerEvent: function(event) {
        return function(e) {
            RiotControl.trigger(event);
        }.bind(this);
    }
});
