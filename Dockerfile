FROM python:3.8.8
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app/
RUN rm -r env/

EXPOSE 8000

ENV FLASK_APP hello
CMD python -m flask run -h 0.0.0.0 -p 8000

