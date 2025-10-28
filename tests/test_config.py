from __future__ import annotations

from pathlib import Path

import pytest

from engine_excel_to_pdf.config import EngineConfig


class TestEngineConfig:
    def test_default_config(self):
        config = EngineConfig()
        
        assert config.output_dir == Path.cwd() / "results"
        assert config.pdfs_subdir == "pdfs"
        assert config.planilhas_subdir == "spreadsheets"
        assert config.dados_subdir == "data"
    
    def test_custom_output_dir(self, temp_dir):
        config = EngineConfig(output_dir=temp_dir)
        
        assert config.output_dir == temp_dir
        assert config.pdfs_dir == temp_dir / "pdfs"
    
    def test_criar_diretorios(self, temp_dir):
        config = EngineConfig(output_dir=temp_dir)
        config.criar_diretorios()
        
        assert config.pdfs_dir.exists()
        assert config.planilhas_dir.exists()
        assert config.dados_dir.exists()
        assert config.logs_dir.exists()
    
    def test_from_dict(self, temp_dir):
        data = {
            "output_dir": str(temp_dir),
            "pdfs_subdir": "custom_pdfs",
        }
        
        config = EngineConfig.from_dict(data)
        
        assert config.output_dir == temp_dir
        assert config.pdfs_subdir == "custom_pdfs"
    
    def test_to_dict(self, temp_dir):
        config = EngineConfig(output_dir=temp_dir)
        
        data = config.to_dict()
        
        assert data["output_dir"] == str(temp_dir)
        assert data["pdfs_subdir"] == "pdfs"
