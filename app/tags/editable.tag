<editable>
    <div class="editable-{ opts.type }">
        <yield/>
    </div>

    this.on('mount', function() {
        console.log($('[property]', this.root));
    });
</editable>
