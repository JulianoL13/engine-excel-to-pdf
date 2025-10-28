from __future__ import annotations

from datetime import date

import pytest

from engine_excel_to_pdf.utils import (
    extract_cnpj,
    format_cnpj,
    normalize_whitespace,
    parse_pt_br_date,
    sanitize_certificate_filename,
    validate_cnpj,
)


class TestNormalizeWhitespace:
    def test_multiple_spaces(self):
        assert normalize_whitespace("hello    world") == "hello world"
    
    def test_tabs_and_newlines(self):
        assert normalize_whitespace("hello\t\nworld") == "hello world"
    
    def test_leading_trailing_spaces(self):
        assert normalize_whitespace("  hello  ") == "hello"


class TestValidateCNPJ:
    def test_valid_cnpj(self):
        assert validate_cnpj("11222333000181") is True
    
    def test_invalid_cnpj_wrong_checksum(self):
        assert validate_cnpj("11222333000182") is False
    
    def test_invalid_cnpj_all_same_digit(self):
        assert validate_cnpj("11111111111111") is False
    
    def test_invalid_cnpj_wrong_length(self):
        assert validate_cnpj("123") is False
    
    def test_empty_cnpj(self):
        assert validate_cnpj("") is False


class TestExtractCNPJ:
    def test_extract_formatted_cnpj(self):
        result = extract_cnpj("CNPJ: 11.222.333/0001-81")
        assert result == "11.222.333/0001-81"
    
    def test_extract_unformatted_cnpj(self):
        result = extract_cnpj("11222333000181")
        assert result == "11.222.333/0001-81"
    
    def test_extract_invalid_cnpj(self):
        result = extract_cnpj("11222333000182")
        assert result is None
    
    def test_extract_no_cnpj(self):
        result = extract_cnpj("sem cnpj aqui")
        assert result is None


class TestFormatCNPJ:
    def test_format_cnpj(self):
        result = format_cnpj("11222333000181")
        assert result == "11.222.333/0001-81"
    
    def test_format_cnpj_invalid_length(self):
        with pytest.raises(ValueError):
            format_cnpj("123")


class TestParsePtBrDate:
    def test_parse_full_month_name(self):
        result = parse_pt_br_date("15 DE JANEIRO DE 2024")
        assert result == date(2024, 1, 15)
    
    def test_parse_different_month(self):
        result = parse_pt_br_date("25 DE DEZEMBRO DE 2024")
        assert result == date(2024, 12, 25)
    
    def test_parse_with_extra_spaces(self):
        result = parse_pt_br_date("  10   DE   MARÇO   DE   2024  ")
        assert result == date(2024, 3, 10)


class TestSanitizeCertificateFilename:
    def test_sanitize_with_slashes(self):
        result = sanitize_certificate_filename("CERT/2024/001")
        assert result == "CERT-2024-001"
    
    def test_sanitize_with_spaces(self):
        result = sanitize_certificate_filename("CERT 2024 001")
        assert result == "CERT-2024-001"
    
    def test_sanitize_with_colons(self):
        result = sanitize_certificate_filename("CERT:2024:001")
        assert result == "CERT-2024-001"
    
    def test_sanitize_multiple_characters(self):
        result = sanitize_certificate_filename("CERT/2024 001:TEST")
        assert result == "CERT-2024-001-TEST"
