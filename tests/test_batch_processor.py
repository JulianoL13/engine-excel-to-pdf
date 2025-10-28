from __future__ import annotations

from pathlib import Path

import pytest
from openpyxl import Workbook

from engine_excel_to_pdf.batch_processor import BatchProcessor


class TestBatchProcessor:
    def test_processar_pasta_sequential(self, temp_dir, sample_excel_file, engine_config, assets_dir):
        engine_config.assets_dir = assets_dir
        from engine_excel_to_pdf.interface import MotorCertificados
        motor = MotorCertificados(config=engine_config)
        
        processor = BatchProcessor(motor=motor, max_workers=None)
        
        pasta_entrada = temp_dir / "entrada"
        pasta_entrada.mkdir()
        
        import shutil
        shutil.copy(sample_excel_file, pasta_entrada / "cert1.xlsx")
        shutil.copy(sample_excel_file, pasta_entrada / "cert2.xlsx")
        
        resultado = processor.processar_pasta(pasta_entrada)
        
        assert resultado["total"] == 2
        assert len(resultado["sucessos"]) == 2
        assert len(resultado["erros"]) == 0
    
    def test_processar_pasta_parallel(self, temp_dir, sample_excel_file, engine_config, assets_dir):
        engine_config.assets_dir = assets_dir
        from engine_excel_to_pdf.interface import MotorCertificados
        motor = MotorCertificados(config=engine_config)
        
        processor = BatchProcessor(motor=motor, max_workers=2)
        
        pasta_entrada = temp_dir / "entrada"
        pasta_entrada.mkdir()
        
        import shutil
        shutil.copy(sample_excel_file, pasta_entrada / "cert1.xlsx")
        shutil.copy(sample_excel_file, pasta_entrada / "cert2.xlsx")
        
        resultado = processor.processar_pasta(pasta_entrada)
        
        assert resultado["total"] == 2
        assert len(resultado["sucessos"]) == 2
    
    def test_processar_pasta_not_found(self, temp_dir, engine_config):
        from engine_excel_to_pdf.interface import MotorCertificados
        motor = MotorCertificados(config=engine_config)
        processor = BatchProcessor(motor=motor)
        
        with pytest.raises(FileNotFoundError):
            processor.processar_pasta(temp_dir / "inexistente")
