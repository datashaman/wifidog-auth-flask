FROM ubuntu:artful

WORKDIR /var/app

RUN apt-get update -q
RUN apt-get install -q -y --no-install-recommends \
    nodejs \
    npm \
    python3.6 \
    python-pip \
    python-setuptools

RUN echo "SQLALCHEMY_DATABASE_URI=sqlite:////var/app/data/local.db" > .env

COPY . ./

RUN pip install -r requirements.txt
RUN npm install .
RUN node_modules/.bin/gulp

EXPOSE 5000

VOLUME /var/app/data

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "-h", "0.0.0.0", "-p", "5000"]
