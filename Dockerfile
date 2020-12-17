FROM python:3.7

COPY ./requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /app

EXPOSE 5000

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]