from __future__ import annotations

from datetime import date, datetime

import pytest

from engine_excel_to_pdf.models import Certificado, MetodoAplicacao, ProdutoQuimico
from engine_excel_to_pdf.validators import CertificadoValidator, ValidationError


class TestValidatePayloadStructure:
    def test_valid_payload_structure(self):
        payload = {
            "certificado": {"numero_certificado": "001"},
            "produtos": [],
            "metodos": [],
        }
        CertificadoValidator.validate_payload_structure(payload)
    
    def test_missing_certificado(self):
        payload = {"produtos": [], "metodos": []}
        with pytest.raises(ValidationError) as exc:
            CertificadoValidator.validate_payload_structure(payload)
        assert "certificado" in str(exc.value)
    
    def test_invalid_produtos_type(self):
        payload = {
            "certificado": {},
            "produtos": "invalid",
            "metodos": [],
        }
        with pytest.raises(ValidationError) as exc:
            CertificadoValidator.validate_payload_structure(payload)
        assert "produtos" in str(exc.value)
    
    def test_invalid_metodos_type(self):
        payload = {
            "certificado": {},
            "produtos": [],
            "metodos": {},
        }
        with pytest.raises(ValidationError) as exc:
            CertificadoValidator.validate_payload_structure(payload)
        assert "metodos" in str(exc.value)


class TestValidateCertificado:
    def test_valid_certificado(self, sample_certificado):
        CertificadoValidator.validate_certificado(sample_certificado)
    
    def test_missing_required_field(self):
        cert = Certificado(
            numero_certificado="",
            numero_licenca="LIC-001",
            razao_social="Empresa",
            nome_fantasia="Fantasia",
            cnpj="11.222.333/0001-81",
            endereco_completo="Rua A",
            data_execucao=date(2024, 1, 1),
            data_validade=date(2024, 12, 31),
            pragas_tratadas="Baratas",
            arquivo_origem="manual",
            data_cadastro=datetime.now(),
        )
        
        with pytest.raises(ValidationError) as exc:
            CertificadoValidator.validate_certificado(cert)
        assert "numero_certificado" in str(exc.value)
    
    def test_invalid_date_range(self):
        cert = Certificado(
            numero_certificado="CERT-001",
            numero_licenca="LIC-001",
            razao_social="Empresa",
            nome_fantasia="Fantasia",
            cnpj="11.222.333/0001-81",
            endereco_completo="Rua A",
            data_execucao=date(2024, 12, 31),
            data_validade=date(2024, 1, 1),
            pragas_tratadas="Baratas",
            arquivo_origem="manual",
            data_cadastro=datetime.now(),
        )
        
        with pytest.raises(ValidationError) as exc:
            CertificadoValidator.validate_certificado(cert)
        assert "before" in str(exc.value).lower()
    
    def test_invalid_cnpj(self):
        cert = Certificado(
            numero_certificado="CERT-001",
            numero_licenca="LIC-001",
            razao_social="Empresa",
            nome_fantasia="Fantasia",
            cnpj="12345678901234",
            endereco_completo="Rua A",
            data_execucao=date(2024, 1, 1),
            data_validade=date(2024, 12, 31),
            pragas_tratadas="Baratas",
            arquivo_origem="manual",
            data_cadastro=datetime.now(),
        )
        
        with pytest.raises(ValidationError) as exc:
            CertificadoValidator.validate_certificado(cert)
        assert "CNPJ" in str(exc.value)


class TestValidateProdutos:
    def test_valid_produtos(self, sample_produtos):
        CertificadoValidator.validate_produtos(sample_produtos)
    
    def test_missing_nome_produto(self):
        produtos = [ProdutoQuimico(nome_produto="", classe_quimica="Classe A", concentracao=1.0)]
        with pytest.raises(ValidationError) as exc:
            CertificadoValidator.validate_produtos(produtos)
        assert "product name" in str(exc.value).lower()
    
    def test_missing_classe_quimica(self):
        produtos = [ProdutoQuimico(nome_produto="Produto A", classe_quimica="", concentracao=1.0)]
        with pytest.raises(ValidationError) as exc:
            CertificadoValidator.validate_produtos(produtos)
        assert "chemical class" in str(exc.value).lower()


class TestValidateMetodos:
    def test_valid_metodos(self, sample_metodos):
        CertificadoValidator.validate_metodos(sample_metodos)
    
    def test_missing_metodo(self):
        metodos = [MetodoAplicacao(metodo="", quantidade="100ml")]
        with pytest.raises(ValidationError) as exc:
            CertificadoValidator.validate_metodos(metodos)
        assert "method" in str(exc.value).lower()
    
    def test_missing_quantidade(self):
        metodos = [MetodoAplicacao(metodo="Pulverização", quantidade="")]
        with pytest.raises(ValidationError) as exc:
            CertificadoValidator.validate_metodos(metodos)
        assert "quantity" in str(exc.value).lower()


class TestValidateBundle:
    def test_valid_bundle(self, sample_bundle):
        CertificadoValidator.validate_bundle(sample_bundle)
