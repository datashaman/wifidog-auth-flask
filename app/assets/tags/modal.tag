<modal>
    <div hidden={ opts.__hidden } class="modal-shade" onclick={ onClose }></div>

    <div hidden={ opts.__hidden } class="modal">
        <div class="modal-heading">
            <button type="button" class="btn btn-close btn-secondary" aria-label="Close" onclick={ onClose }>
                <span aria-ishidden="true">&times;</span>
            </button>

            <h3 class="modal-title">{ opts.heading }</h3>
        </div>

        <div class="modal-body">
            <yield />
        </div>
    </div>

    <style scoped>
        .modal-shade {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            z-index: 50;
            cursor: pointer;
        }

        .modal {
            position: absolute;
            width: 95%;
            max-width: 500px;
            font-size: 1.1em;
            top: 50%;
            left: 50%;
            transform: translate3d(-50%, -50%, 0);
            background-color: white;
            color: #252519;
            z-index: 101;
        }

        .modal-heading {
            position: relative;
            text-align: center;
        }

        .modal-title {
            padding: 20px 20px 0 20px;
            margin: 0;
            font-size: 1.2em;
        }

        .modal-body {
            padding: 20px;
        }

        .modal-footer {
            padding: 0 20px 20px 20px;
        }

        .btn-close {
            float: right;
            margin: 5px 5px 0 0;
        }

        .clear {
            clear: both;
        }
    </style>

    this.on('mount', function() {
        // Move modal to bottom of body so it renders correctly
        $(this.root).remove().appendTo('body');

        // Attach escape key to cancel
        $(document).keyup(function(e) {
            if(e.keyCode == 27) {
                this.onClose();
            }
        }.bind(this));
    });

    onClose() {
        RiotControl.trigger(this.opts.cancelevent);
    }
</modal>
