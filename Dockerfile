FROM python:3.6-slim-jessie

WORKDIR /var/app

RUN pip install dotenvy fabric jinja2

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

EXPOSE 5000

VOLUME /var/app/data

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "-h", "0.0.0.0", "-p", "5000"]
