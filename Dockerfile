FROM python:3.6-slim-jessie

WORKDIR /var/app

RUN pip install dotenvy fabric jinja2

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

ENV HOST=0.0.0.0 PORT=8080
EXPOSE 8080

CMD python serve.py
