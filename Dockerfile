FROM ubuntu:artful

ARG XDG_CACHE_HOME=/cache

WORKDIR /var/app

RUN apt-get update -q \
    && apt-get install -q -y --no-install-recommends \
        curl \
        nodejs \
        npm \
        python-pip \
        python-setuptools \
        tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN echo "SQLALCHEMY_DATABASE_URI=sqlite:////var/app/data/local.db" > .env

COPY \
    config.py \
    gulpfile.js \
    healthcheck.sh \
    manage.py \
    package.json \
    package-lock.json \
    requirements.txt \
    ./

RUN pip install -r requirements.txt && rm requirements.txt
RUN npm config set cache "${XDG_CACHE_HOME}/npm" && npm install

COPY auth/assets auth/assets/

RUN node_modules/.bin/gulp && rm -rf auth/assets gulpfile.js node_modules package.json package-lock.json

COPY auth auth/

RUN rm -rf /tmp/* /usr/share/doc /usr/share/info

EXPOSE 5000

VOLUME ["/var/app/data", "/var/app/auth/static/uploads"]

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "-h", "0.0.0.0", "-p", "5000"]
