#!/usr/bin/env bash
set -euo pipefail

API_KEY="${API_KEY:-dev_key_1}"

curl -sS -X POST http://localhost:8080/ingest   -H "Content-Type: application/json"   -H "X-API-Key: ${API_KEY}"   -d '{
    "user_email": "alice@example.org",
    "app_id": "thunderbird-plugin-iaassistant",
    "message": "export carnet contacts terminé",
    "attributes": {"count": 42, "result": "ok"}
  }' | jq .
