function render(attribute) {
    switch(typeof attribute) {
        case 'object':
            if (typeof attribute.$date != 'undefined') {
                var date = new Date(attribute.$date);
                return date.toLocaleString();
            }

            if (typeof attribute.$ref != 'undefined') {
                return attribute.$ref.replace(/^.*\//, '');
            }
            break;
        default:
            return attribute;
    }
}
