riot.mixin('render', {
    render: function(attribute) {
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
    },

    renderTime: function(dt) {
        if (dt) {
            dt = new Date(dt.$date);
            return this.pad(dt.getHours(), 2) + ':' + this.pad(dt.getMinutes(), 2);
        }
    },

    pad: function(number, length) {
        var str = '' + number;

        while (str.length < length) {
            str = '0' + str;
        }

        return str;
    }

});
