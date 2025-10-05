!/bin/bash
set -e

echo "Starting ingestion process..."
python app/ingest.py

# exec "$@" # will execut CMD from Dockerfile without logging.
gunicorn --bind=0.0.0.0:9696 --chdir=app --log-level=debug server:app