Zepto(function($) {
    $('table[data-sortable]').each(function () {
        var $table = $(this);
        var $tbody = $table.find('tbody');

        $table.find('thead tr').prepend('<td></td>');
        $table.find('tfoot tr').prepend('<td></td>');
        $table.find('.sequence').hide();
        $tbody.find('tr').prepend('<td class="sortable-handle"><span class="oi" data-glyph="elevator" title="Sort" aria-hidden="true"></span></td>');
        $tbody.each(function () {
            var url = $(this).data('url');

            Sortable.create(this, {
                animation: 150,
                handle: '.sortable-handle',
                onUpdate: function (evt) {
                    var sequences = {};
                    $tbody.find('tr').each(function (index) {
                        sequences[$(this).data('id')] = index * 10;
                    });
                    $.ajax({
                        type: 'POST',
                        url: url,
                        contentType: 'application/json',
                        data: JSON.stringify({ sequences: sequences })
                    });
                }
            });
        });
    });
});
