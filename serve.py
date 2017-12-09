import os

from auth import create_app
app = create_app()

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=int(app.config['PORT']))
