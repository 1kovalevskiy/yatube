FROM python:3.8

WORKDIR /code
COPY requirements.txt .
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY yatube/. .
CMD gunicorn yatube.wsgi:application --bind 0.0.0.0:8000