"""
Pramana AI Strict-RAG Backend API.
Entrypoint for Bali DigiFest 2026 AI Web Innovation Challenge.
"""

import logging
import os
import threading
import time
from typing import Dict, List, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.models.schemas import (
    TripBriefRequest,
    TripBriefResponse,
    ContextNoteRequest,
    ContextNoteResponse,
    CorpusResponse,
    ZoneListResponse,
    ZoneCardResponse,
    ZoneBriefRequest,
    ZoneBriefResponse,
)
from backend.services.calendar_service import CALENDAR_COVERAGE
from backend.services.rag_engine import PUBLIC_BASE_URL, StrictRAGEngine
from backend.services.corpus_loader import CorpusManager
from backend.services.zone_registry import ZoneNotFoundError
from backend.services import ai_metrics
from backend.services.ai_config import (
    GEMINI_MODEL,
    ai_enabled,
    get_ai_mode,
    get_gemini_api_key,
    get_gemini_model_chain,
)

logger = logging.getLogger("pramana")

APP_VERSION = "1.4.0"
RATE_LIMIT_PATHS = {"/api/v1/trip-brief", "/api/v1/context-note"}
RATE_LIMIT_POST_PREFIXES = ("/api/v1/totem/",)
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60"))
MAX_REQUEST_BODY_BYTES = int(os.getenv("MAX_REQUEST_BODY_BYTES", "65536"))
TRUST_PROXY_HEADERS = os.getenv("TRUST_PROXY_HEADERS", "true").strip().lower() in {
    "1", "true", "yes", "on",
}

_rate_lock = threading.Lock()
_rate_buckets: Dict[str, List[float]] = {}


def _allowed_origins() -> List[str]:
    raw = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://pramana1.vercel.app",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _client_key(request: Request) -> str:
    # 1. Client-provided session id header takes priority if present
    session_id = request.headers.get("x-session-id", "").strip()
    if session_id:
        return f"session:{session_id}"
    # 2. X-Forwarded-For when proxy headers trusted
    if TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _allow_request(client_key: str) -> bool:
    """Small in-memory sliding-window limiter for expensive POST endpoints."""
    now = time.monotonic()
    with _rate_lock:
        bucket = [
            timestamp
            for timestamp in _rate_buckets.get(client_key, [])
            if now - timestamp < RATE_LIMIT_WINDOW_SECONDS
        ]
        if len(bucket) >= RATE_LIMIT_MAX_REQUESTS:
            _rate_buckets[client_key] = bucket
            return False

        bucket.append(now)
        _rate_buckets[client_key] = bucket

        # Prevent unbounded growth from many distinct client keys.
        if len(_rate_buckets) > 10000:
            stale_keys = [
                key for key, timestamps in _rate_buckets.items()
                if not timestamps or now - timestamps[-1] >= RATE_LIMIT_WINDOW_SECONDS
            ]
            for key in stale_keys:
                _rate_buckets.pop(key, None)

        return True


app = FastAPI(
    title="Pramana Strict-RAG API",
    version=APP_VERSION,
    description=(
        "Deterministic legal retrieval and abstention-first compliance "
        "assistance for Bali tourism. Output is educational, not legal advice."
    ),
)

# CORS is environment-driven. Wildcard origins are not combined with
# credentials, which browsers reject anyway.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=600,
)

rag_engine = StrictRAGEngine()
corpus_manager = CorpusManager.get_instance()


@app.middleware("http")
async def security_and_rate_limit(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_REQUEST_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Ukuran permintaan melebihi batas / Request payload exceeds maximum allowed size."},
                )
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Header Content-Length tidak valid / Invalid Content-Length header."},
            )

    if request.method == "POST" and (
        request.url.path in RATE_LIMIT_PATHS
        or (
            request.url.path.startswith(RATE_LIMIT_POST_PREFIXES)
            and request.url.path.endswith("/brief")
        )
    ):
        if not _allow_request(_client_key(request)):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        "Terlalu banyak permintaan. Silakan coba lagi dalam satu menit / Rate limit exceeded. Please try again in 1 minute."
                    )
                },
                headers={"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
            )

    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=()"
    )

    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'"
        )

    return response


@app.api_route("/", methods=["GET", "HEAD"])
@app.api_route("/health", methods=["GET", "HEAD"])
@app.api_route("/api/v1/health", methods=["GET", "HEAD"])
def healthcheck():
    stats = corpus_manager.get_stats()
    return {
        "status": "healthy",
        "service": "pramana-strict-rag",
        "version": APP_VERSION,
        "total_regulations_indexed": stats["total_regulations_indexed"],
        "total_documents_registered": stats["total_documents_registered"],
        "total_manifest_documents": stats["total_manifest_documents"],
        "corpus_version": corpus_manager.metadata.get("version"),
        "corpus_last_verified_date": corpus_manager.metadata.get(
            "last_verified_date"
        ),
        "total_smart_gate_zones": len(rag_engine.zone_registry.get_all()),
        "smart_gate_version": rag_engine.zone_registry.metadata.get("version"),
        "ai_mode": get_ai_mode(),
        "ai_enabled": ai_enabled(),
        "ai_model": GEMINI_MODEL,
        "calendar_coverage": CALENDAR_COVERAGE,
        "verification_scope": "corpus",
    }


@app.get("/api/v1/ai/status")
def ai_status():
    """Return AI runtime telemetry without prompts, responses, or PII."""
    data = ai_metrics.snapshot()
    stats = corpus_manager.get_stats()
    data["ai_mode"] = get_ai_mode()
    data["model_name"] = GEMINI_MODEL
    data["model_chain"] = get_gemini_model_chain()
    data["api_key_configured"] = bool(get_gemini_api_key())
    data["active_chunks_count"] = stats["total_regulations_indexed"]
    data["registry_docs_count"] = 4
    data["registry_only_documents"] = [
        "se-gubernur-bali-7-2025",
        "se-kapolri-6-2015",
        "skb-ite-2021",
        "awig-awig-desa-adat-penglipuran",
    ]
    data["epistemic_routing_enabled"] = True
    data["hybrid_retrieval_available"] = rag_engine.hybrid.available
    data["embedding_vectors_loaded"] = rag_engine.hybrid.vector_count
    return data


@app.get("/api/v1/corpus", response_model=CorpusResponse)
def get_corpus():
    """Return registered regulations and legal tier metadata for UI transparency."""
    return {
        "metadata": corpus_manager.metadata,
        "tiers": corpus_manager.tiers,
        "regulations": corpus_manager.get_all(),
        "documents": corpus_manager.get_documents(),
    }


@app.get("/api/v1/zones", response_model=ZoneListResponse)
def get_zones():
    """Return the Smart Gate zone directory."""
    data = rag_engine.list_zones()
    data["public_base_url"] = PUBLIC_BASE_URL
    return data


@app.get("/api/v1/totem/{zone_id}", response_model=ZoneCardResponse)
def get_totem_card(
    zone_id: str,
    lang: Literal["id", "en"] = "id",
):
    """Return one deterministic Smart Gate card with verified citations."""
    try:
        card = rag_engine.get_zone_card(zone_id, lang)
        card["public_base_url"] = PUBLIC_BASE_URL
        return card
    except ZoneNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        logger.exception("totem card processing failed")
        raise HTTPException(
            status_code=500,
            detail=(
                "Terjadi kesalahan internal saat memuat kartu gerbang / Internal error loading smart gate card."
            ),
        )


@app.post("/api/v1/totem/{zone_id}/brief", response_model=ZoneBriefResponse)
def generate_totem_brief(zone_id: str, req: ZoneBriefRequest):
    """Generate a grounded AI brief for one Smart Gate zone."""
    try:
        return rag_engine.analyze_zone_brief(zone_id, req.lang)
    except ZoneNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        logger.exception("totem brief processing failed")
        raise HTTPException(
            status_code=500,
            detail=(
                "Terjadi kesalahan internal saat menyusun panduan gerbang / Internal error generating smart gate brief."
            ),
        )


@app.post("/api/v1/trip-brief", response_model=TripBriefResponse)
def generate_trip_brief(req: TripBriefRequest):
    """
    Mode 1: Generate an itinerary-based compliance briefing.
    Detects Nyepi conflicts, retrieves relevant corpus articles, and formats
    WhatsApp / ICS outputs. Abstains when retrieval is not grounded.
    """
    try:
        return rag_engine.analyze_trip_itinerary(
            itinerary_text=req.itinerary_text,
            start_date=req.start_date,
            end_date=req.end_date,
            traveler_origin=req.traveler_origin,
            lang=req.lang,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        logger.exception("trip-brief processing failed")
        raise HTTPException(
            status_code=500,
            detail=(
                "Terjadi kesalahan internal saat memproses trip brief / Internal error processing trip brief."
            ),
        )


@app.post("/api/v1/context-note", response_model=ContextNoteResponse)
def generate_context_note(req: ContextNoteRequest):
    """
    Mode 2: Generate a neutral, verifiable Context Note for viral content.
    Identifies legal grounds, emotional framing, and returns corpus citations.
    """
    try:
        return rag_engine.analyze_viral_post(post_content=req.post_content, lang=req.lang)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        logger.exception("context-note processing failed")
        raise HTTPException(
            status_code=500,
            detail=(
                "Terjadi kesalahan internal saat memproses catatan konteks / Internal error processing context note."
            ),
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)
