from __future__ import annotations

import os
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent

STORAGE_ROOT = Path(os.getenv("ENGINE_STORAGE_ROOT", PROJECT_ROOT / "motor_certificados"))
DATA_DIR = STORAGE_ROOT / "dados"
PLANILHAS_DIR = STORAGE_ROOT / "saidas" / "planilhas"
PDFS_DIR = STORAGE_ROOT / "saidas" / "pdfs"
LOG_DIR = STORAGE_ROOT / "logs"
LOG_FILE = LOG_DIR / "processamento.log"

ASSETS_DIR = Path(os.getenv("ENGINE_ASSETS_DIR", PROJECT_ROOT / "assets"))
DEFAULT_LOGO_PATH = ASSETS_DIR / "logo.png"
TEMPLATES_DIR = ASSETS_DIR / "templates"


def ensure_directories() -> None:
    """Ensure all necessary directories exist."""
    for path in (DATA_DIR, PLANILHAS_DIR, PDFS_DIR, LOG_DIR, ASSETS_DIR, TEMPLATES_DIR):
        path.mkdir(parents=True, exist_ok=True)
