from __future__ import annotations

from datetime import date, datetime

import pytest

from engine_excel_to_pdf.models import Certificado, CertificadoBundle, MetodoAplicacao, ProdutoQuimico


class TestCertificado:
    def test_create_certificado(self):
        cert = Certificado(
            numero_certificado="CERT-001",
            numero_licenca="LIC-001",
            razao_social="Empresa",
            nome_fantasia="Fantasia",
            cnpj="12.345.678/0001-90",
            endereco_completo="Rua A, 123",
            data_execucao=date(2024, 1, 1),
            data_validade=date(2024, 12, 31),
            pragas_tratadas="Baratas",
            arquivo_origem="manual",
            data_cadastro=datetime.now(),
        )
        
        assert cert.numero_certificado == "CERT-001"
        assert cert.razao_social == "Empresa"
        assert cert.id is not None
        assert len(cert.id) == 12


class TestProdutoQuimico:
    def test_create_produto_with_concentracao(self):
        produto = ProdutoQuimico(
            nome_produto="Produto A",
            classe_quimica="Classe A",
            concentracao=2.5,
        )
        
        assert produto.nome_produto == "Produto A"
        assert produto.concentracao == 2.5
    
    def test_create_produto_without_concentracao(self):
        produto = ProdutoQuimico(
            nome_produto="Produto B",
            classe_quimica="Classe B",
            concentracao=None,
        )
        
        assert produto.concentracao is None
    
    def test_from_dict(self):
        data = {
            "nome_produto": "Produto C",
            "classe_quimica": "Classe C",
            "concentracao": 1.5,
        }
        produto = ProdutoQuimico.from_dict(data)
        
        assert produto.nome_produto == "Produto C"
        assert produto.concentracao == 1.5


class TestMetodoAplicacao:
    def test_create_metodo(self):
        metodo = MetodoAplicacao(
            metodo="Pulverização",
            quantidade="100ml",
        )
        
        assert metodo.metodo == "Pulverização"
        assert metodo.quantidade == "100ml"
    
    def test_from_dict(self):
        data = {
            "metodo": "Gel",
            "quantidade": "50g",
        }
        metodo = MetodoAplicacao.from_dict(data)
        
        assert metodo.metodo == "Gel"
        assert metodo.quantidade == "50g"


class TestCertificadoBundle:
    def test_create_bundle(self, sample_certificado, sample_produtos, sample_metodos):
        bundle = CertificadoBundle(
            certificado=sample_certificado,
            produtos=sample_produtos,
            metodos=sample_metodos,
        )
        
        assert bundle.certificado == sample_certificado
        assert len(bundle.produtos) == 2
        assert len(bundle.metodos) == 2
