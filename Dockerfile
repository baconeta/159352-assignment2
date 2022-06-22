FROM python:3.10-slim-bullseye
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY requirements.txt $WORKDIR

RUN pip install -r requirements.txt

COPY . /app/
RUN rm -r env/

ENV FLASK_APP flightbookingapp
CMD python -m flask run -h 0.0.0.0 -p 8000