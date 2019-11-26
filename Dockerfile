FROM python:3.7-alpine
COPY requirements.txt /
RUN apk add --update alpine-sdk
RUN pip install -r /requirements.txt
COPY src/ /app
WORKDIR /app
CMD ["python3", "/app/main.py"]