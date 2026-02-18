FROM python:3.10.11-slim-buster

WORKDIR /app

COPY . /app

COPY phishfiner phishfiner

RUN pip install -r requirements.txt

RUN pip install evidently==0.4.17

CMD [ "python3","app.py" ]