from app import create_app

[ application, datastore ] = create_app()

if __name__ == '__main__':
    application.run(debug=True, host=application.config['HOST'], port=int(application.config['PORT']))
