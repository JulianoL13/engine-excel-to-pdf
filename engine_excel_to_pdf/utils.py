from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional, TYPE_CHECKING

from dateutil import parser

if TYPE_CHECKING:
    from .models import Certificado

_PT_BR_MONTHS = {
    "JANEIRO": "January",
    "FEVEREIRO": "February",
    "MARÇO": "March",
    "ABRIL": "April",
    "MAIO": "May",
    "JUNHO": "June",
    "JULHO": "July",
    "AGOSTO": "August",
    "SETEMBRO": "September",
    "OUTUBRO": "October",
    "NOVEMBRO": "November",
    "DEZEMBRO": "December",
}

_CNPJ_RE = re.compile(r"(\d{2})\.?\d{3}\.\d{3}/\d{4}-\d{2}")
_NON_DIGIT_RE = re.compile(r"\D")


def normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def extract_cnpj(value: str) -> Optional[str]:
    """Extract and validate CNPJ with checksum verification.
    
    Args:
        value: String potentially containing a CNPJ
        
    Returns:
        Formatted CNPJ if valid, None otherwise
    """
    match = _CNPJ_RE.search(value)
    if match:
        cnpj = match.group(0)
        digits = _NON_DIGIT_RE.sub("", cnpj)
        if validate_cnpj(digits):
            return format_cnpj(digits)
        return None
    
    digits = _NON_DIGIT_RE.sub("", value)
    if len(digits) == 14 and validate_cnpj(digits):
        return format_cnpj(digits)
    return None


def validate_cnpj(cnpj: str) -> bool:
    """Validate CNPJ checksum digits.
    
    Args:
        cnpj: 14-digit CNPJ string (digits only)
        
    Returns:
        True if CNPJ is valid, False otherwise
    """
    if not cnpj or len(cnpj) != 14:
        return False
    
    if cnpj == cnpj[0] * 14:
        return False
    
    weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_1 = sum(int(cnpj[i]) * weights_1[i] for i in range(12))
    digit_1 = 11 - (sum_1 % 11)
    digit_1 = 0 if digit_1 >= 10 else digit_1
    
    if int(cnpj[12]) != digit_1:
        return False
    
    weights_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_2 = sum(int(cnpj[i]) * weights_2[i] for i in range(13))
    digit_2 = 11 - (sum_2 % 11)
    digit_2 = 0 if digit_2 >= 10 else digit_2
    
    return int(cnpj[13]) == digit_2


def format_cnpj(digits: str) -> str:
    digits = _NON_DIGIT_RE.sub("", digits)
    if len(digits) != 14:
        raise ValueError("CNPJ precisa de 14 dígitos")
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


def parse_pt_br_date(value: str) -> date:
    normalized = normalize_whitespace(value).upper()
    for pt_month, en_month in _PT_BR_MONTHS.items():
        if pt_month in normalized:
            normalized = normalized.replace(pt_month, en_month)
    normalized = normalized.replace(" DE ", " ")
    normalized = normalized.replace("  ", " ")
    parsed = parser.parse(normalized, dayfirst=True)
    return parsed.date()


def pick_first(values: Iterable[Optional[str]]) -> Optional[str]:
    for value in values:
        if value:
            return value
    return None


def sanitize_certificate_filename(value: str) -> str:
    """
    Sanitize a certificate number or value for use in filenames.
    
    Args:
        value: The value to sanitize
        
    Returns:
        Sanitized string safe for filenames
    """
    sanitized = normalize_whitespace(value)
    for char in ("/", "\\", " ", ":"):
        sanitized = sanitized.replace(char, "-")
    return sanitized


def generate_unique_filename(certificado: "Certificado", extensao: str = "") -> str:
    """
    Generate a unique filename using: nome_fantasia + CNPJ + numero_certificado + timestamp.
    
    This prevents file overwrites when multiple certificates share the same certificate number.
    Format: nome-fantasia_CNPJ_numero-cert_YYYYMMDD-HHMMSS.ext
    
    Args:
        certificado: Certificate object containing the data
        extensao: File extension (with or without dot)
        
    Returns:
        Unique sanitized filename
    """
    nome_fantasia = sanitize_certificate_filename(certificado.nome_fantasia or "sem-nome")
    nome_fantasia = nome_fantasia[:30]
    
    cnpj_digits = re.sub(r'\D', '', certificado.cnpj or "")
    cnpj_short = cnpj_digits[:8] if cnpj_digits else "00000000"
    
    numero_cert = sanitize_certificate_filename(certificado.numero_certificado)
    
    timestamp = certificado.data_cadastro.strftime("%Y%m%d-%H%M%S")
    id_suffix = (certificado.id or "")[:4]
    
    if not extensao.startswith(".") and extensao:
        extensao = f".{extensao}"
    
    suffix = f"-{id_suffix}" if id_suffix else ""
    return f"{nome_fantasia}_{cnpj_short}_{numero_cert}_{timestamp}{suffix}{extensao}"


def ensure_path(path_like) -> Path:
    """
    Convert path-like object to Path and ensure parent directories exist.
    
    Args:
        path_like: String, Path, or path-like object
        
    Returns:
        Normalized Path object
    """
    path = Path(path_like)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
