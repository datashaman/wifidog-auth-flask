FROM okdocker/pynode:latest

ARG BUILD_HOME=/var/app/build

WORKDIR /var/app

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
RUN yarn install --frozen-lockfile

COPY auth/assets auth/assets/

RUN node_modules/.bin/gulp && rm -rf auth/assets gulpfile.js node_modules package.json package-lock.json yarn.lock

COPY auth auth/
COPY data/reference.db data/
COPY settings settings/

RUN rm -rf \
    /root/.cache \
    /tmp/* \
    /usr/share/doc \
    /usr/share/info \
    /var/lib/apt/lists/*

EXPOSE 5000

VOLUME ["/var/app/build", "/var/app/instance"]

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "-h", "0.0.0.0", "-p", "5000"]
