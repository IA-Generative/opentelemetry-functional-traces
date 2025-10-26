import os
import hmac
import hashlib
from typing import Optional, Dict, Any

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, EmailStr
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

OTLP_GRPC_ENDPOINT = os.getenv("OTLP_GRPC_ENDPOINT", "otel-collector:4317")
HASH_SALT = os.getenv("HASH_SALT", "dev-salt-change-me").encode("utf-8")
API_KEYS = [k.strip() for k in os.getenv("API_KEYS", "dev_key_1").split(",") if k.strip()]
LOG_LEVEL = os.getenv("GATEWAY_LOG_LEVEL", "INFO")

resource = Resource.create({
    "service.name": "functional-trace-gateway",
    "service.version": "0.1.0"
})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=f"http://{OTLP_GRPC_ENDPOINT}", insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = FastAPI(title="Functional Trace Gateway")

class IngestBody(BaseModel):
    user_email: EmailStr
    app_id: str
    message: str
    attributes: Optional[Dict[str, Any]] = None

def email_hash(email: str) -> str:
    normalized = email.strip().lower().encode("utf-8")
    return hmac.new(HASH_SALT, normalized, hashlib.sha256).hexdigest()

def validate_api_key(api_key: Optional[str]) -> str:
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key")
    if api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.post("/ingest")
async def ingest(body: IngestBody, request: Request, x_api_key: Optional[str] = Header(default=None)):
    key = validate_api_key(x_api_key)
    user_h = email_hash(body.user_email)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    key_id = key[-6:] if len(key) >= 6 else key

    with tracer.start_as_current_span("functional_event") as span:
        span.set_attribute("user.hash", user_h)
        span.set_attribute("app.id", body.app_id)
        span.set_attribute("event.message", body.message)
        if client_ip:
            span.set_attribute("client.ip", client_ip)
        if user_agent:
            span.set_attribute("http.user_agent", user_agent)
        span.set_attribute("client.api_key_id", key_id)

        if body.attributes:
            for k, v in body.attributes.items():
                # Avoid overwriting reserved keys
                if k in {"user.hash", "app.id", "event.message", "client.api_key_id"}:
                    span.set_attribute(f"attr.{k}", v)
                else:
                    span.set_attribute(k, v)

    return {"status": "ok", "user_hash": user_h, "app_id": body.app_id}
