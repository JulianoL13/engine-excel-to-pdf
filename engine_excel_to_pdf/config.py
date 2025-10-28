from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class EngineConfig:
    """
    Customizable engine configuration.
    
    Allows users to define where results will be saved.
    """

    output_dir: Path = field(default_factory=lambda: Path.cwd() / "results")

    pdfs_subdir: str = "pdfs"
    planilhas_subdir: str = "spreadsheets"
    dados_subdir: str = "data"
    logs_subdir: str = "logs"

    assets_dir: Optional[Path] = None
    logo_path: Optional[Path] = None
    template_name: str = "certificado.html"
    stylesheet_name: str = "certificado.css"

    sobrescrever_existentes: bool = False
    validar_cnpj: bool = True
    criar_backup: bool = False

    @property
    def pdfs_dir(self) -> Path:
        """Directory where PDFs will be saved."""
        return self.output_dir / self.pdfs_subdir

    @property
    def planilhas_dir(self) -> Path:
        """Directory where spreadsheets will be saved."""
        return self.output_dir / self.planilhas_subdir

    @property
    def dados_dir(self) -> Path:
        """Directory where CSV data files will be saved."""
        return self.output_dir / self.dados_subdir

    @property
    def logs_dir(self) -> Path:
        """Directory where logs will be saved."""
        return self.output_dir / self.logs_subdir

    def criar_diretorios(self) -> None:
        """Create all necessary directories."""
        for diretorio in [
            self.pdfs_dir,
            self.planilhas_dir,
            self.dados_dir,
            self.logs_dir,
        ]:
            diretorio.mkdir(parents=True, exist_ok=True)

        if self.assets_dir:
            self.assets_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_dict(cls, config: dict) -> EngineConfig:
        """Create configuration from dictionary."""
        if "output_dir" in config and isinstance(config["output_dir"], str):
            config["output_dir"] = Path(config["output_dir"])
        if "assets_dir" in config and isinstance(config["assets_dir"], str):
            config["assets_dir"] = Path(config["assets_dir"])
        if "logo_path" in config and isinstance(config["logo_path"], str):
            config["logo_path"] = Path(config["logo_path"])

        return cls(**config)

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "output_dir": str(self.output_dir),
            "pdfs_subdir": self.pdfs_subdir,
            "planilhas_subdir": self.planilhas_subdir,
            "dados_subdir": self.dados_subdir,
            "logs_subdir": self.logs_subdir,
            "assets_dir": str(self.assets_dir) if self.assets_dir else None,
            "logo_path": str(self.logo_path) if self.logo_path else None,
            "template_name": self.template_name,
            "stylesheet_name": self.stylesheet_name,
            "sobrescrever_existentes": self.sobrescrever_existentes,
            "validar_cnpj": self.validar_cnpj,
            "criar_backup": self.criar_backup,
        }
