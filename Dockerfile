FROM python:3.11-slim

WORKDIR /app

COPY server.py /app/
COPY static /app/static

RUN pip install flask flask-cors

EXPOSE 5000

CMD ["python", "server.py"]
