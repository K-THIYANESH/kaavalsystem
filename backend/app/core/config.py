"""Global configuration for the KAAVAL backend."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings  # type: ignore

from pydantic import Field
try:
    # Pydantic v2
    from pydantic import field_validator  # type: ignore
    FIELD_VALIDATOR_AVAILABLE = True
except Exception:
    FIELD_VALIDATOR_AVAILABLE = False
    from pydantic import validator  # type: ignore


class Settings(BaseSettings):
    """Pydantic settings object loaded from env variables when available."""

    app_name: str = "KAAVAL AI Platform"
    api_prefix: str = "/api"
    version: str = "1.0.0"

    # Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2])
    database_path: Path = Field(default_factory=lambda: Path("database/kaaval.db"))
    uploads_dir: Path = Field(default_factory=lambda: Path("uploads"))
    logs_dir: Path = Field(default_factory=lambda: Path("logs"))
    models_dir: Path = Field(default_factory=lambda: Path("models"))
    reports_dir: Path = Field(default_factory=lambda: Path("reports"))

    # Google Maps
    google_maps_api_key: str = Field("", env="GOOGLE_MAPS_API_KEY")

    # Feature toggles
    enable_hierarchical_filter: bool = True
    enable_quality_selector: bool = True
    enable_coarse_to_fine: bool = True
    enable_faiss_gpu: bool = True
    enable_temporal_tracker: bool = True
    enable_specialist_selector: bool = True
    enable_age_progression: bool = True

    # Performance controls
    frame_skip_interval: int = 3
    adaptive_frame_skip_max: int = 6
    quality_threshold: float = 0.3
    adaptive_top_k_frames: int = 127
    stage1_top_k: int = 500
    stage2_top_k: int = 50
    final_top_k: int = 5

    # Hardware - GPU enabled by default (PyTorch CUDA installed)
    use_gpu: bool = True
    torch_device: str = "cuda"
    gpu_memory_fraction: float = 0.85

    # Torch device selection: use pydantic v2 `field_validator` when available,
    # otherwise fall back to legacy `validator` for pydantic v1.
    if FIELD_VALIDATOR_AVAILABLE:
        @field_validator("torch_device", mode="before")
        def set_torch_device(cls, v, info):
            if not getattr(cls, "use_gpu", True):
                return "cpu"
            return v
    else:
        @validator("torch_device", pre=True, always=True)
        def set_torch_device(cls, v: str, values: dict) -> str:
            if not values.get("use_gpu", False):
                return "cpu"
            return v

    # Background workers
    worker_concurrency: int = 4
    task_queue: str = "redis://localhost:6379/0"

    # Telemetry & logging
    enable_telemetry: bool = True
    telemetry_interval_seconds: int = 30
    structured_logging: bool = True

    # Strictness: require a reconstruction model to be present at startup
    require_reconstruction_model: bool = True

    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    api_base_url: str = "http://localhost:8000/api"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

    if FIELD_VALIDATOR_AVAILABLE:
        @field_validator("database_path", "uploads_dir", "logs_dir", "models_dir", "reports_dir", mode="before")
        def _ensure_path(cls, v, info):
            path = Path(v)
            if not path.is_absolute():
                path = Path(__file__).resolve().parents[2] / path
            return path
    else:
        @validator("database_path", "uploads_dir", "logs_dir", "models_dir", "reports_dir", pre=True)
        def _ensure_path(cls, value: str | Path) -> Path:  # noqa: D401
            path = Path(value)
            if not path.is_absolute():
                path = Path(__file__).resolve().parents[2] / path
            return path


@lru_cache()
def get_settings() -> Settings:
    """Return a cached instance of the settings object."""

    settings = Settings()
    for directory in (
        settings.uploads_dir,
        settings.logs_dir,
        settings.models_dir,
        settings.reports_dir,
        settings.database_path.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
