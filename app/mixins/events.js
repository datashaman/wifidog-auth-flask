riot.mixin('events', {
    triggerEvent: function(event) {
        console.log('here');
        return function(e) {
            RiotControl.trigger(event);
        }.bind(this);
    }
});
