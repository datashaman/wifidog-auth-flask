riot.mixin('currentuser', {
    init: function() {
        RiotControl.on('currentuser.loaded', function (currentuser) {
            this.currentuser = currentuser;
            this.update();
        }.bind(this));

        RiotControl.trigger('currentuser.load');
    },

    hasRole: function(role) {
        return this.currentuser.roles.indexOf(role) > -1;
    }

});
