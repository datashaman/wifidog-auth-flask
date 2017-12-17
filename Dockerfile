FROM python:3.6-slim-jessie

ARG BUILD_HOME=/var/app/build

WORKDIR /var/app

RUN apt-get update -q \
    && apt-get install -q -y --no-install-recommends \
        wget

RUN wget -O - https://deb.nodesource.com/setup_8.x | bash -

RUN apt-get install -q -y --no-install-recommends \
        nodejs \
        tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN echo "SQLALCHEMY_DATABASE_URI=sqlite:////var/app/data/local.db" > .env

COPY \
    deploy.sh \
    gulpfile.js \
    healthcheck.sh \
    manage.py \
    package.json \
    package-lock.json \
    ./

COPY build build/

RUN ./deploy.sh
RUN npm install

COPY auth/assets auth/assets/

RUN node_modules/.bin/gulp && rm -rf auth/assets gulpfile.js node_modules package.json package-lock.json

COPY auth auth/
COPY data/reference.db data/
COPY settings settings/

RUN rm -rf /tmp/* /usr/share/doc /usr/share/info

EXPOSE 5000

VOLUME ["/var/app/build", "/var/app/data", "/var/app/auth/static/uploads"]

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "-h", "0.0.0.0", "-p", "5000"]
