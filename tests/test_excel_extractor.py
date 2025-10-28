from __future__ import annotations

import pytest

from engine_excel_to_pdf.extractor.excel_extractor import ExcelExtractor


class TestExcelExtractor:
    def test_extract_from_excel(self, sample_excel_file):
        extractor = ExcelExtractor()
        
        bundle = extractor.extract(sample_excel_file)
        
        assert bundle.certificado.numero_certificado == "CERT-2024-001"
        assert bundle.certificado.numero_licenca == "LIC-SP-12345"
        assert bundle.certificado.razao_social == "Empresa Teste LTDA"
        assert bundle.certificado.cnpj == "11.222.333/0001-81"
        assert len(bundle.produtos) == 2
        assert len(bundle.metodos) == 2
    
    def test_extract_produtos(self, sample_excel_file):
        extractor = ExcelExtractor()
        bundle = extractor.extract(sample_excel_file)
        
        assert bundle.produtos[0].nome_produto == "Inseticida Alpha"
        assert bundle.produtos[0].classe_quimica == "Piretroide"
        assert bundle.produtos[0].concentracao == 2.5
        
        assert bundle.produtos[1].nome_produto == "Raticida Beta"
        assert bundle.produtos[1].concentracao == 0.005
    
    def test_extract_metodos(self, sample_excel_file):
        extractor = ExcelExtractor()
        bundle = extractor.extract(sample_excel_file)
        
        assert bundle.metodos[0].metodo == "Pulverização"
        assert bundle.metodos[0].quantidade == "500ml"
        
        assert bundle.metodos[1].metodo == "Gel"
        assert bundle.metodos[1].quantidade == "50g"
