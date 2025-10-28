from __future__ import annotations

from datetime import date

import pytest

from engine_excel_to_pdf.interface import MotorCertificados
from engine_excel_to_pdf.validators import ValidationError


class TestMotorCertificados:
    def test_processar_upload(self, engine_config, sample_excel_file, assets_dir):
        engine_config.assets_dir = assets_dir
        motor = MotorCertificados(config=engine_config)
        
        resultado = motor.processar_upload(sample_excel_file)
        
        assert "certificado" in resultado
        assert "planilha" in resultado
        assert "pdf" in resultado
        assert resultado["certificado"].numero_certificado == "CERT-2024-001"
        assert resultado["planilha"].exists()
        assert resultado["pdf"].exists()
    
    def test_criar_manual(self, engine_config, assets_dir):
        engine_config.assets_dir = assets_dir
        motor = MotorCertificados(config=engine_config)
        
        payload = {
            "certificado": {
                "numero_certificado": "CERT-MANUAL-001",
                "numero_licenca": "LIC-001",
                "razao_social": "Empresa Manual LTDA",
                "nome_fantasia": "Manual Corp",
                "cnpj": "11.222.333/0001-81",
                "endereco_completo": "Rua Manual, 456",
                "data_execucao": date(2024, 2, 1),
                "data_validade": date(2024, 8, 1),
                "pragas_tratadas": "Cupins",
            },
            "produtos": [
                {
                    "nome_produto": "Cupinicida",
                    "classe_quimica": "Organofosforado",
                    "concentracao": 1.5,
                }
            ],
            "metodos": [
                {
                    "metodo": "Injeção",
                    "quantidade": "200ml",
                }
            ],
        }
        
        resultado = motor.criar_manual(payload)
        
        assert resultado["certificado"].numero_certificado == "CERT-MANUAL-001"
        assert resultado["planilha"].exists()
        assert resultado["pdf"].exists()
    
    def test_criar_manual_invalid_payload(self, engine_config):
        motor = MotorCertificados(config=engine_config)
        
        payload = {"produtos": [], "metodos": []}
        
        with pytest.raises(ValidationError):
            motor.criar_manual(payload)
    
    def test_exportar_certificado(self, engine_config, sample_excel_file, assets_dir):
        engine_config.assets_dir = assets_dir
        motor = MotorCertificados(config=engine_config)
        motor.processar_upload(sample_excel_file)
        
        resultado = motor.exportar_certificado("CERT-2024-001")
        
        assert resultado is not None
        assert resultado["certificado"].numero_certificado == "CERT-2024-001"
    
    def test_exportar_certificado_not_found(self, engine_config):
        motor = MotorCertificados(config=engine_config)
        
        resultado = motor.exportar_certificado("INEXISTENTE")
        
        assert resultado is None
    
    def test_listar_certificados(self, engine_config, sample_excel_file, assets_dir):
        engine_config.assets_dir = assets_dir
        motor = MotorCertificados(config=engine_config)
        motor.processar_upload(sample_excel_file)
        
        certificados = motor.listar_certificados()
        
        assert len(certificados) == 1
        assert certificados[0].numero_certificado == "CERT-2024-001"
