FROM python:3.6-slim-jessie

ARG BUILD_HOME=/var/app/build

WORKDIR /var/app

RUN apt-get update -q \
    && apt-get install -q -y --no-install-recommends \
        curl

RUN curl -L https://deb.nodesource.com/setup_8.x | bash -

RUN apt-get install -q -y --no-install-recommends \
        nodejs \
        tzdata

RUN curl -L https://yarnpkg.com/install.sh | bash -

COPY \
    deploy.sh \
    gulpfile.js \
    healthcheck.sh \
    manage.py \
    package.json \
    package-lock.json \
    yarn.lock \
    ./

COPY build build/

RUN ./deploy.sh
RUN /root/.yarn/bin/yarn

COPY auth/assets auth/assets/

RUN node_modules/.bin/gulp && rm -rf auth/assets gulpfile.js node_modules package.json package-lock.json

COPY auth auth/
COPY data/reference.db data/
COPY settings settings/

RUN rm -rf \
    /tmp/* \
    /usr/share/doc \
    /usr/share/info \
    /var/lib/apt/lists/*

EXPOSE 5000

VOLUME ["/var/app/build", "/var/app/instance"]

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "-h", "0.0.0.0", "-p", "5000"]
