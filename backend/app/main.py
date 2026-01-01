"""Entry point for the KAAVAL FastAPI application."""

from __future__ import annotations

import json
import logging
import time
import sys
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import api_router
from .core.config import settings
from .core.init_db import init_db
from .telemetry.metrics import register_metrics


def _configure_performance_logging(app: FastAPI) -> None:
    """Attach middleware that records request latency to a rotating log."""

    log_path = settings.logs_dir / "performance.log"
    logger = logging.getLogger("kaaval.performance")
    if not logger.handlers:
        # Ensure file handler uses UTF-8 to avoid encoding errors on Windows consoles
        handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    @app.middleware("http")
    async def log_request_performance(request: Request, call_next):  # type: ignore
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        payload = {
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        }
        logger.info(json.dumps(payload))
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
        return response


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    app = FastAPI(title=settings.app_name, version=settings.version)

    # CORS - Allow frontend to access backend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8001",
            "http://127.0.0.1:8001",
            "*"  # Allow all origins for development
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )

    register_metrics(app)

    # Try to ensure console streams use UTF-8 to avoid 'charmap' encoding failures
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        # Best-effort only; continue if platform does not support reconfigure
        pass

    _configure_performance_logging(app)

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.on_event("startup")
    async def startup_event():
        """Initialize database and check resources on startup."""
        logging.info("Initializing database...")
        try:
            init_db()
            logging.info("Database initialized successfully.")
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
        
        # Check for models
        missing_models = []
        required_models = ["retinaface.onnx", "arcface_resnet100.onnx", "attribute_net.onnx", "gfpgan.pth"]
        for model in required_models:
            if not (settings.models_dir / model).exists():
                missing_models.append(model)

        if missing_models:
            logging.warning(f"MISSING MODELS: {', '.join(missing_models)}")
            logging.warning("Some features will not work until models are downloaded.")

        # Check reconstruction model presence (mandatory if configured)
        recon_candidates = [
            settings.models_dir / "gfpgan.pth",
            settings.models_dir / "stylegan2_age.pt",
            settings.models_dir / "stylegan2-ada.pth",
            settings.models_dir / "stylegan2-ada.pkl",
        ]
        recon_found = any(p.exists() for p in recon_candidates)
        if not recon_found:
            msg = (
                "No reconstruction model found in models directory. "
                "Place one of (gfpgan.pth, stylegan2_age.pt, stylegan2-ada.*) in the models folder."
            )
            if settings.require_reconstruction_model:
                logging.error(msg)
                raise RuntimeError(msg)
            else:
                logging.warning(msg)


    @app.get("/healthz")
    async def health_check():
        """Health check endpoint for monitoring."""
        return {"status": "ok", "version": settings.version}

    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": settings.app_name,
            "version": settings.version,
            "api_docs": "/docs",
            "health": "/healthz",
        }

    return app


app = create_app()

