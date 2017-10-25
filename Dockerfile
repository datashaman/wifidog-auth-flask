FROM python:3.6.3-slim-jessie

WORKDIR /var/app

RUN apt-get update && \
    apt-get install -yq --no-install-recommends \
        fabric \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install dotenvy

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

ENV HOST=0.0.0.0 PORT=8080
EXPOSE 8080

CMD python serve.py
