FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9696

ENTRYPOINT ["bash", "start_server.sh", "setup_dbs=true", "setup_grafana=true"]