import requests
import json
import os
import sys

# --- Configuration ---
# Grafana API access details
GRAFANA_URL = os.environ.get("GRAFANA_URL", "http://localhost:3000")
GRAFANA_USER = "admin"
GRAFANA_PASSWORD = "admin"
DASHBOARD_FILE = "grafana/dashboard3.json"
DATASOURCE_NAME = "LocalPostgresDS26"

# Postgres connection details
# NOTE ON DOCKER: If Grafana and Postgres are running in the SAME Docker network,
# you should use the POSTGRES_HOST (the container name or network alias)
# instead of 'localhost' or '127.0.0.1'.
# If they are both exposed on the host machine, 'localhost' might work.
POSTGRES_HOST = "postgres"  # Change this to your Postgres container name or IP
POSTGRES_PORT = 5432
POSTGRES_DATABASE = "conversations_db"
POSTGRES_USER = "user"
POSTGRES_PASSWORD = "user"
# ---------------------

def delete_datascource(ds_name):

    api_endpoint = f"{GRAFANA_URL}/api/datasources/name/{ds_name}"
    auth = (GRAFANA_USER, GRAFANA_PASSWORD)

    try:
        requests.delete(
            api_endpoint,
            headers={"Content-Type": "application/json"},
            auth=auth
        )
    except requests.exceptions.RequestException as e:
        print(f"❌ Error deleting data source: {e}")
        return False
    

def create_datasource():
    """Creates a new PostgreSQL data source in Grafana."""
    print(f"Attempting to create data source: {DATASOURCE_NAME}...")

    api_endpoint = f"{GRAFANA_URL}/api/datasources"
    auth = (GRAFANA_USER, GRAFANA_PASSWORD)

    # Payload defining the PostgreSQL data source
    datasource_payload = {
        "name": DATASOURCE_NAME,
        "type": "postgres",
        "access": "proxy", # Required access mode
        "isDefault": False,
        "url": f"{POSTGRES_HOST}:{POSTGRES_PORT}",
        "database": POSTGRES_DATABASE,
        "user": POSTGRES_USER,
        "tlsSkipVerify": True,
        "secureJsonData": {
            "password": POSTGRES_PASSWORD
        },
        "jsonData": {
            # Disable SSL for local Docker setup, change if needed
            "sslmode": "disable",
            "tlsAuth": False,
            "tlsAuthWithCACert": False,
            "tlsSkipVerify": True,
            "database": POSTGRES_DATABASE,
        }
    }

    try:
        response = requests.post(
            api_endpoint,
            headers={"Content-Type": "application/json"},
            auth=auth,
            json=datasource_payload
        )
        
        response.raise_for_status()

        if response.status_code == 200:
            print(f"✅ Data source '{DATASOURCE_NAME}' created successfully.")
            ds_uid = response.json()['datasource']['uid']
            print(f"Grafana datasource UID: {ds_uid}")
            return ds_uid
        elif response.status_code == 409 and "Data source with same name already exists" in response.text:
            print(f"⚠️ Data source '{DATASOURCE_NAME}' already exists. Skipping creation.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating data source: {e}")
        if '401 Client Error' in str(e):
             print("   -> Check GRAFANA_USER and GRAFANA_PASSWORD in the script.")
        elif 'Name or service not known' in str(e) or 'Failed to establish a new connection' in str(e):
            print(f"   -> Check if Grafana is running at {GRAFANA_URL}.")
        return None
    except json.JSONDecodeError:
        print(f"❌ API response was not valid JSON: {response.text}")
        return None

    return None


def upload_dashboard(filepath, ds_uid):
    """Uploads a dashboard JSON file to Grafana."""
    if not os.path.exists(filepath):
        print(f"❌ Error: Dashboard file not found at '{filepath}'.")
        return False

    print(f"Attempting to upload dashboard from: {filepath}...")

    api_endpoint = f"{GRAFANA_URL}/api/dashboards/db"
    auth = (GRAFANA_USER, GRAFANA_PASSWORD)

    try:
        with open(filepath, 'r') as f:
            f = f.read().replace('${DS_UID}', ds_uid)
            dashboard_content = json.loads(f)

        # The Grafana API expects the dashboard content to be nested,
        # along with control flags like 'overwrite' and 'folderId'.
        # 'overwrite: True' allows updating an existing dashboard with the same UID.
        upload_payload = {
            "dashboard": dashboard_content,
            "folderId": 0, # General folder
            "overwrite": True
        }

    except json.JSONDecodeError:
        print(f"❌ Error: Failed to parse '{filepath}'. Ensure it is valid JSON.")
        return False
    except IOError as e:
        print(f"❌ Error reading file: {e}")
        return False

    try:
        response = requests.post(
            api_endpoint,
            headers={"Content-Type": "application/json"},
            auth=auth,
            json=upload_payload
        )
        response.raise_for_status()

        response_data = response.json()

        if response_data.get('status') == 'success':
            print(f"✅ Dashboard '{response_data}' uploaded successfully.")
            return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Error uploading dashboard: {e}")
        if response.text:
            print(f"   -> Grafana response details: {response.text}")
        return False


def main():
    """Main function to execute the setup steps."""
    print("--- Grafana Automated Setup Script ---")

    # 1. Create Data Source
    delete_datascource(DATASOURCE_NAME)
    ds_uid = create_datasource()
    if ds_uid == None:
        print("Setup aborted due to data source creation failure.")
        sys.exit(1)

    # 2. Upload Dashboard
    if not upload_dashboard(DASHBOARD_FILE, ds_uid):
        print("Setup aborted due to dashboard upload failure.")
        sys.exit(1)

    print("\n🎉 Grafana setup complete!")


if __name__ == "__main__":
    main()
