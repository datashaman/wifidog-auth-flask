FROM ubuntu:artful

WORKDIR /var/app

RUN apt-get update -q && \
    apt-get install -q -y --no-install-recommends \
        nodejs \
        npm \
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
    ./

COPY auth auth/

RUN pip install -r requirements.txt && rm -rf /root/.cache requirements.txt
RUN npm install && rm -rf /root/.npm
RUN node_modules/.bin/gulp && rm -rf auth/assets gulpfile.js node_modules package.json package-lock.json
RUN rm -rf /tmp/* /usr/share/doc /usr/share/info

EXPOSE 5000

VOLUME ["/var/app/data", "/var/app/uploads"]

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "-h", "0.0.0.0", "-p", "5000"]
