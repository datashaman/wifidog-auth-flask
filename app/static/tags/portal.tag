<portal about="/api/gateway/{{ gateway.id }}">
    <ul class="actions">
        <button if={ mode == 'display' } onclick={ onEdit }>Edit</button>
        <button if={ mode == 'edit' } onclick={ onDisplay }>Display</button>
    </ul>

    <div class="header">
        <property if={ mode == 'edit' || gateway.logo } name="logo" type="file" url="/static/logos" value={ gateway.logo }>
            <img src="/static/logos/{ opts.value }" />
        </property>

        <property name="title" value={ gateway.title }>
            <h1>{ opts.value }</h1>
        </property>

        <property if={ mode == 'edit' || gateway.subtitle } name="subtitle" value={ gateway.subtitle } placeholder="subtitle">
            <h2>{ opts.value || '' }</h2>
        </property>
    </div>

    <div class="content">
        <h2 if={ mode == 'edit' || gateway.subhead } property="subhead" class="content-subhead">{ gateway.subhead }</h2>

        <property name="description" type="textarea" translate="marked" value={ gateway.description }>
            { opts.value }
        </property>

        <div if={ mode == 'display' } property="url_facebook"
            class="fb-like"
            data-href={ gateway.url_facebook }
            data-width="300"
            data-layout="standard"
            data-action="like"
            data-show-faces="true"
            data-share="true">
        </div>
    </div>

    onEdit() {
        this.mode = 'edit';
    }

    onDisplay() {
        this.mode = 'display';
    }

    RiotControl.on('gateway.loaded', function(gateway) {
        this.gateway = gateway;
        this.update();
    }.bind(this));

    RiotControl.trigger('gateway.load', opts.gateway);

    this.mode = opts.mode || 'display';
</portal>
