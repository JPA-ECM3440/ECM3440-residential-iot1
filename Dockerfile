FROM docker.io/python:3

WORKDIR /usr/src/app

COPY soil-moisture-sensor/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./soil-moisture-sensor .

CMD [ "python", "./app.py" ]
