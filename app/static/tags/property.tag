<property>
    <div style="width: { opts.width || 'auto' }; height: { opts.height || 'auto' }">
        <div if={ parent.mode == 'display' } name="display" class="display">
            <yield />
        </div>

        <div if={ parent.mode == 'edit' } class="edit">
            <input if={ this.type == 'text' } type="text" name="edit" value={ opts.value } placeholder={ opts.placeholder || '' } />
            <textarea if={ this.type == 'textarea' } name="edit">{ opts.value }</textarea>

            <div if={ this.type == 'file' }>
                <img if={ opts.value } src={ opts.url + '/' + opts.value } />
                <input if={ this.type == 'file' } type="file" name="edit" onchange={ onChangeFile } />
            </div>
        </div>
    </div>

    <style scoped>
    .button-xs {
        font-size: 30%;
    }
    .display {
        padding: 10px;
    }
    .display, .edit {
        width: 100%;
        height: 100%;
    }
    .edit textarea {
        padding: 10px;
        width: 100%;
        height: 100%;
    }
    </style>

    onChangeFile(e) {
        var xhr = new XMLHttpRequest(),
            about = $(e.target).closest('[about]').attr('about');
            fd = new FormData();

        fd.append('file', e.target.files[0]);
        xhr.open('post', about + '/' + this.name);
        console.log(xhr.send(fd));
    }

    this.name = opts.name;
    this.type = opts.type || 'text';

    this.on('update', function() {
        if (opts.value !== undefined && opts.translate) {
            var func = window[opts.translate];
            this.display.innerHTML = func(opts.value);
        }
    });
</property>
