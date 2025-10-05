# !/bin/bash
set -e

SETUP_DBS="false"
SETUP_GRAFANA="false"

setup_databases() {
  echo "---Starting DB ingestion process..."
  sleep 6
  python app/setup_dbs.py
}

setup_monitoring() {
  echo "---Starting Grafana setup process..."
  python grafana/init_grafana.py
}

start_application() {
  echo "--- 🚀 Starting iDelivery Support Backend Server ---"
  gunicorn --bind=0.0.0.0:9696 --chdir=app --log-level=debug server:app
}

for arg in "$@"; do
    case "$arg" in
        setup_dbs=*)
            SETUP_DBS="${arg#*=}"
            ;;
        setup_grafana=*)
            SETUP_GRAFANA="${arg#*=}"
            ;;
        *)
            echo "Warning: Ignoring unknown argument: $arg. Use key=value format."
            ;;
    esac
done

echo "-----------------------------------------------------"
echo "iDelivery Courier Support Platform Deployment Script"
echo "Database Setup Requested: $SETUP_DBS"
echo "Grafana Setup Requested: $SETUP_GRAFANA"
echo "-----------------------------------------------------"

if [ "$SETUP_DBS" == "true" ]; then
    setup_databases
fi

if [ "$SETUP_GRAFANA" == "true" ]; then
    setup_monitoring
fi

start_application

echo "-----------------------------------------------------"
echo "Application stopped."
