<modal>
    <div class="overlay { hidden, ghost, dismissable }" onclick={ onclose }></div>

    <div class="modal { hidden, ghost, dismissable }">
        <div class="header">
            <button if={ dismissable } type="button" class="close" aria-label="Close" onclick={ onclose }>
                <span aria-hidden="true">&times;</span>
            </button>

            <h3 class="heading">{ heading }</h3>
        </div>

        <div class="body">
            <yield />
        </div>
    </div>

    <style scoped>
        .overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            z-index: 50;
        }

        .overlay.dismissable {
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

        .modal.ghost {
            background-color: transparent;
            color: white;
        }

        .header {
            position: relative;
            text-align: center;
        }

        .heading {
            padding: 20px 20px 0 20px;
            margin: 0;
            font-size: 1.2em;
        }

        .modal.ghost .heading {
            color: white;
        }

        .close {
            position: absolute;
            top: 5px;
            right: 10px;
            padding: 0;
            font-size: 1.2em;
            border: 0;
            background-color: transparent;
            color: #000;
            cursor: pointer;
            outline: none;
        }

        .modal.ghost .close {
            color: white;
        }

        .body {
            padding: 20px;
        }

        .footer {
            padding: 0 20px 20px 20px;
        }

        .button {
            float: right;
            padding: 10px;
            margin: 0 5px 0 0;
            border: none;
            font-size: 0.9em;
            text-transform: uppercase;
            cursor: pointer;
            outline: none;
            background-color: white;
        }

        .modal.ghost .button {
            color: white;
            background-color: transparent;
        }

        .clear {
            clear: both;
        }

    </style>

    this.hidden = opts.hidden;
    this.heading = opts.heading;
    this.ghost = opts.ghost;
    this.dismissable = opts.dismissable;
    this.onclose = opts.onclose;
</modal>
