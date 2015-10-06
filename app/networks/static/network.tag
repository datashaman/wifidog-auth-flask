<network>
    <h1>Network: { network.title }</h1>

    <form class="pure-form pure-form-stacked">
        <legend>Network Details</legend>
        {{ render_field(form.email, class='pure-input-1', placeholder='Email') }}
    </form>

    <div class="actions-collection">
        <form class="pure-form" onsubmit={ doNothing }>
            <fieldset>
                <button type="submit" class="pure-button" onclick={ remove }>
                    <span class="oi" data-glyph="x" title="Remove" aria-hidden="true"></span>
                    Remove
                </button>
            </fieldset>
        </form>
    </div>

    <script>
    var self = this;

    RiotControl.on('network.updated', function (network) {
        self.network = network;
        self.update();
    });

    RiotControl.trigger('network.load');

    renderDateTime(dt) {
        if (dt) {
            dt = new Date(dt);
            return dt.toLocaleString();
        }
    }

    doNothing(e) {
        return false;
    }
    </script>
</network>
