FROM python:3.12-slim-bookworm

ENV BOT_TOKEN=""

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app

CMD ["python", "main.py"]
