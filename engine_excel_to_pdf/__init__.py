"""
Engine Excel to PDF - Certificate extraction, validation and generation engine.

Main components:
- CertificateEngine (MotorCertificados): Main interface for processing
- BatchProcessor: Batch processing of multiple files
- EngineConfig: Customizable directory and option configuration
- Models: Dataclasses for data representation
- Validators: Business rule validation
- Generators: PDF and spreadsheet generation
"""

from .batch_processor import BatchProcessor, ProcessingResult
from .config import EngineConfig
from .interface import MotorCertificados
from .models import Certificado, CertificadoBundle, MetodoAplicacao, ProdutoQuimico
from .validators import CertificadoValidator, ValidationError

CertificateEngine = MotorCertificados

__version__ = "0.1.0"

__all__ = [
    "CertificateEngine",
    "BatchProcessor",
    "ProcessingResult",
    "EngineConfig",
    "Certificado",
    "CertificadoBundle",
    "ProdutoQuimico",
    "MetodoAplicacao",
    "CertificadoValidator",
    "ValidationError",
    "MotorCertificados",
]
