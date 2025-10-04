FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9696

ENTRYPOINT ["sh", "start_server.sh"]

# CMD ["gunicorn", "--bind=0.0.0.0:9696", "--chdir=app", "--log-level=info", "server:app"]