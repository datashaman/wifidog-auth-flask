FROM python:3.6-slim-jessie

WORKDIR /var/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN echo "SQLALCHEMY_DATABASE_URI=sqlite:////var/app/data/local.db" > .env

COPY . ./

EXPOSE 5000

VOLUME /var/app/data

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "-h", "0.0.0.0", "-p", "5000"]
