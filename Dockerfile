FROM ubuntu:artful

WORKDIR /var/app

RUN apt-get update -q && \
    apt-get install -q -y --no-install-recommends \
        nodejs \
        npm \
        python3.6 \
        python-pip \
        python-setuptools && \
    rm -rf /var/lib/apt/lists/*

RUN echo "SQLALCHEMY_DATABASE_URI=sqlite:////var/app/data/local.db" > .env

COPY \
    config.py \
    gulpfile.js \
    manage.py \
    package.json \
    package-lock.json \
    requirements.txt \
    yarn.lock \
    ./

COPY app app/

RUN pip install -r requirements.txt && rm -rf /root/.cache
RUN npm install . && rm -rf /root/.npm
RUN node_modules/.bin/gulp

EXPOSE 5000

VOLUME /var/app/data

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "-h", "0.0.0.0", "-p", "5000"]
