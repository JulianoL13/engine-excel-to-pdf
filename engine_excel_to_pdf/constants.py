"""Constants used throughout the application."""

from __future__ import annotations

from enum import Enum


class FileOrigin(str, Enum):
    """Source of certificate data."""
    MANUAL = "entrada-manual"
    EXCEL_UPLOAD = "upload-excel"


class CSVFile(str, Enum):
    """CSV file names for data storage."""
    CERTIFICATES = "certificados.csv"
    PRODUCTS = "produtos_quimicos.csv"
    METHODS = "metodos_aplicacao.csv"


class OutputDir(str, Enum):
    """Output directory names."""
    DATA = "dados"
    OUTPUTS = "saidas"
    SPREADSHEETS = "planilhas"
    PDFS = "pdfs"
    LOGS = "logs"


DEFAULT_PLACEHOLDER = "--"
CERTIFICATE_PREFIX = "certificado-"

EXCEL_COLUMN_WIDTH_DEFAULT = 25
EXCEL_COLUMN_WIDTH_WIDE = 30
EXCEL_FREEZE_PANES_CELL = "A2"

FILE_ORIGIN_MANUAL = FileOrigin.MANUAL.value
FILE_ORIGIN_EXCEL = FileOrigin.EXCEL_UPLOAD.value
CSV_CERTIFICATES = CSVFile.CERTIFICATES.value
CSV_PRODUCTS = CSVFile.PRODUCTS.value
CSV_METHODS = CSVFile.METHODS.value
DIR_DATA = OutputDir.DATA.value
DIR_OUTPUTS = OutputDir.OUTPUTS.value
DIR_SPREADSHEETS = OutputDir.SPREADSHEETS.value
DIR_PDFS = OutputDir.PDFS.value
DIR_LOGS = OutputDir.LOGS.value
