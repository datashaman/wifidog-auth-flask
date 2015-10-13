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
    }
});
