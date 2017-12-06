FROM ubuntu:artful

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

COPY \
    config.py \
    gulpfile.js \
    healthcheck.sh \
    manage.py \
    package.json \
    package-lock.json \
    requirements.txt \
    ./

COPY auth auth/

RUN pip install -r requirements.txt && rm requirements.txt
RUN npm config set cache ${XDG_CACHE_HOME}/npm && npm install
RUN node_modules/.bin/gulp && rm -rf auth/assets gulpfile.js node_modules package.json package-lock.json
RUN rm -rf /tmp/* /usr/share/doc /usr/share/info

EXPOSE 5000

VOLUME ["/var/app/data", "/var/app/uploads"]

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "-h", "0.0.0.0", "-p", "5000"]
