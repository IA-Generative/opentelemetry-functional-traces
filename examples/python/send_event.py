import os, requests

API_KEY = os.getenv("API_KEY", "dev_key_1")
payload = {
    "user_email": "alice@example.org",
    "app_id": "py-script-demo",
    "message": "synchronisation dossier envoyés effectuée",
    "attributes": {"synced": True, "items": 128}
}

r = requests.post(
    "http://localhost:8080/ingest",
    headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
    json=payload,
    timeout=10
)
print(r.status_code, r.text)
