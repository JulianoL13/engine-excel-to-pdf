from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from engine_excel_to_pdf.interface import MotorCertificados
from engine_excel_to_pdf.config import EngineConfig


def test_manual_same_origin_same_number_generates_two_pdfs(temp_dir, assets_dir):
    config = EngineConfig(output_dir=temp_dir)
    config.assets_dir = assets_dir
    motor = MotorCertificados(config=config)

    payload_base = {
        "certificado": {
            "numero_certificado": "CERT-ANUAL-2025",
            "numero_licenca": "LIC-SP-12345",
            "razao_social": "CAMINO SUPERMERCADOS",
            "nome_fantasia": "CAMINO CAROLINA",
            "cnpj": "11.222.333/0001-81",
            "endereco_completo": "Rua A, 123, Bairro, Cidade-SP",
            "data_execucao": "2025-08-10",
            "data_validade": "2026-08-10",
            "pragas_tratadas": "Insetos",
        }
    }

    # Primeiro certificado
    r1 = motor.criar_manual(payload_base)
    pdf1 = r1["pdf"]
    assert pdf1.exists()

    # Segundo certificado, mesmo numero e mesmo arquivo_origem (implícito)
    payload2 = {
        "certificado": {
            **payload_base["certificado"],
            "nome_fantasia": "CAMINO ESTREITO",
        }
    }
    r2 = motor.criar_manual(payload2)
    pdf2 = r2["pdf"]
    assert pdf2.exists()

    # Deve gerar arquivos distintos
    assert pdf1 != pdf2
    assert pdf1.name != pdf2.name

