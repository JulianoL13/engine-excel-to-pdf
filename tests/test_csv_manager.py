from __future__ import annotations

from pathlib import Path

import pytest

from engine_excel_to_pdf.storage.csv_manager import CsvManager


class TestCsvManager:
    def test_init_creates_files(self, temp_dir):
        manager = CsvManager(data_dir=temp_dir)
        
        assert manager.certificados_path.exists()
        assert manager.produtos_path.exists()
        assert manager.metodos_path.exists()
    
    def test_append_bundle(self, temp_dir, sample_bundle):
        manager = CsvManager(data_dir=temp_dir)
        
        certificado = manager.append_bundle(sample_bundle)
        
        assert certificado.id is not None
        assert len(certificado.id) == 12
        assert manager.certificados_path.read_text().count("\n") == 2
    
    def test_append_multiple_bundles(self, temp_dir, sample_certificado, sample_produtos, sample_metodos):
        from engine_excel_to_pdf.models import CertificadoBundle, Certificado
        import copy
        from datetime import datetime, timedelta
        
        manager = CsvManager(data_dir=temp_dir)
        
        cert1_data = copy.deepcopy(sample_certificado)
        cert1_data.numero_certificado = "CERT-001"
        cert1_data.arquivo_origem = "arquivo1.xlsx"
        cert1_data.data_cadastro = datetime.now()
        cert1_data.id = None
        cert1_data.id = cert1_data._generate_id()
        bundle1 = CertificadoBundle(cert1_data, sample_produtos, sample_metodos)
        
        cert2_data = copy.deepcopy(sample_certificado)
        cert2_data.numero_certificado = "CERT-002"
        cert2_data.arquivo_origem = "arquivo2.xlsx"
        cert2_data.data_cadastro = datetime.now() + timedelta(seconds=1)
        cert2_data.id = None
        cert2_data.id = cert2_data._generate_id()
        bundle2 = CertificadoBundle(cert2_data, sample_produtos, sample_metodos)
        
        result1 = manager.append_bundle(bundle1)
        result2 = manager.append_bundle(bundle2)
        
        assert result1.id is not None
        assert result2.id is not None
        assert result1.id != result2.id
    
    def test_get_bundle_by_numero(self, temp_dir, sample_bundle):
        manager = CsvManager(data_dir=temp_dir)
        manager.append_bundle(sample_bundle)
        
        retrieved = manager.get_bundle_by_numero("CERT-2024-001")
        
        assert retrieved is not None
        assert retrieved.certificado.numero_certificado == "CERT-2024-001"
        assert len(retrieved.produtos) == 2
        assert len(retrieved.metodos) == 2
    
    def test_get_bundle_not_found(self, temp_dir):
        manager = CsvManager(data_dir=temp_dir)
        
        retrieved = manager.get_bundle_by_numero("INEXISTENTE")
        
        assert retrieved is None
    
    def test_list_certificados(self, temp_dir, sample_bundle):
        manager = CsvManager(data_dir=temp_dir)
        manager.append_bundle(sample_bundle)
        
        certificados = manager.list_certificados()
        
        assert len(certificados) == 1
        assert certificados[0].numero_certificado == "CERT-2024-001"
    
    def test_skip_duplicate_by_arquivo_origem(self, temp_dir, sample_bundle):
        """Test that processing same file twice doesn't create duplicate."""
        manager = CsvManager(data_dir=temp_dir)
        
        result1 = manager.append_bundle(sample_bundle, skip_if_exists=True)
        result2 = manager.append_bundle(sample_bundle, skip_if_exists=True)
        
        assert result1.id == result2.id
        
        certificados = manager.list_certificados()
        assert len(certificados) == 1
    
    def test_allow_duplicate_when_skip_disabled(self, temp_dir, sample_bundle):
        """Test that duplicates are allowed when skip_if_exists=False."""
        from datetime import datetime, timedelta
        import copy
        
        manager = CsvManager(data_dir=temp_dir)
        
        bundle1 = copy.deepcopy(sample_bundle)
        bundle1.certificado.data_cadastro = datetime.now()
        bundle1.certificado.id = None
        
        bundle2 = copy.deepcopy(sample_bundle)
        bundle2.certificado.data_cadastro = datetime.now() + timedelta(seconds=1)
        bundle2.certificado.id = None
        
        result1 = manager.append_bundle(bundle1, skip_if_exists=False)
        result2 = manager.append_bundle(bundle2, skip_if_exists=False)
        
        assert result1.id != result2.id
        
        certificados = manager.list_certificados()
        assert len(certificados) == 2
    
    def test_get_bundle_by_arquivo(self, temp_dir, sample_bundle):
        """Test retrieving bundle by source file name."""
        manager = CsvManager(data_dir=temp_dir)
        manager.append_bundle(sample_bundle)
        
        retrieved = manager.get_bundle_by_arquivo("upload-excel")
        
        assert retrieved is not None
        assert retrieved.certificado.arquivo_origem == "upload-excel"
        assert len(retrieved.produtos) == 2
        assert len(retrieved.metodos) == 2
    
    def test_get_bundle_by_arquivo_not_found(self, temp_dir):
        """Test that non-existent file returns None."""
        manager = CsvManager(data_dir=temp_dir)
        
        retrieved = manager.get_bundle_by_arquivo("nao-existe.xlsx")
        
        assert retrieved is None
