#!/usr/bin/env bash
set -euo pipefail

API_KEY="${API_KEY:-my_secret_key_1234}"

curl -vvv -sS -X POST http://localhost:8080/ingest   -H "Content-Type: application/json"   -H "X-API-Key: ${API_KEY}"   -d '{
    "user_email": "alice@example.org",
    "app_id": "thunderbird-plugin-iaassistant",
    "message": "lancement de l'"'"'application",
    "attributes": {"count": 42, "result": "ok"}
  }' | jq .

sleep 0.25
curl -vvv -sS -X POST http://localhost:8080/ingest   -H "Content-Type: application/json"   -H "X-API-Key: ${API_KEY}"   -d '{
    "user_email": "alice@example.org",
    "app_id": "thunderbird-plugin-iaassistant",
    "message": "lancement du plug-in IA Assistant",
    "attributes": {"count": 42, "result": "ok"}
  }' | jq .

sleep 0.25

curl -vvv -sS -X POST http://localhost:8080/ingest   -H "Content-Type: application/json"   -H "X-API-Key: ${API_KEY}"   -d '{
    "user_email": "alice@example.org",
    "app_id": "thunderbird-plugin-iaassistant",
    "message": "erreur lors du lancement du plug-in IA Assistant",
    "attributes": {"count": 42, "result": "ok"}
  }' | jq .

sleep 0.25

curl -vvv -sS -X POST http://localhost:8080/ingest   -H "Content-Type: application/json"   -H "X-API-Key: ${API_KEY}"   -d '{
    "user_email": "alice@example.org",
    "app_id": "thunderbird-plugin-iaassistant",
    "message": "appel llm pour générer un email",
    "attributes": {"count": 42, "result": "ok"}
  }' | jq .

sleep 0.25

curl -vvv -sS -X POST http://localhost:8080/ingest   -H "Content-Type: application/json"   -H "X-API-Key: ${API_KEY}"   -d '{
    "user_email": "alice@example.org",
    "app_id": "thunderbird-plugin-iaassistant",
    "message": "appel menu",
    "attributes": {"count": 42, "result": "ok"}
  }' | jq .
