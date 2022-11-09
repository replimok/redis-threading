FROM python:3.9-alpine

WORKDIR /src

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "main.py"]
