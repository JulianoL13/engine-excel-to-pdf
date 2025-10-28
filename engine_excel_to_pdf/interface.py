from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .config import EngineConfig
from .extractor.excel_extractor import ExcelExtractor
from .generators.pdf_generator import PDFGenerator
from .generators.spreadsheet_generator import SpreadsheetGenerator
from .models import Certificado, CertificadoBundle, MetodoAplicacao, ProdutoQuimico
from .config_defaults import ensure_directories
from .storage.csv_manager import CsvManager
from .validators import CertificadoValidator, ValidationError
from .constants import FILE_ORIGIN_MANUAL


class MotorCertificados:
    def __init__(
        self,
        config: Optional[EngineConfig] = None,
        extractor: Optional[ExcelExtractor] = None,
        csv_manager: Optional[CsvManager] = None,
        spreadsheet_generator: Optional[SpreadsheetGenerator] = None,
        pdf_generator: Optional[PDFGenerator] = None,
        skip_validation: bool = False,
    ) -> None:
        self.config = config or EngineConfig()
        self.config.criar_diretorios()
        self.skip_validation = skip_validation
        
        if config:
            self.extractor = extractor or ExcelExtractor()
            self.csv_manager = csv_manager or CsvManager(data_dir=self.config.dados_dir)
            self.spreadsheet_generator = spreadsheet_generator or SpreadsheetGenerator(
                output_dir=self.config.planilhas_dir
            )
            self.pdf_generator = pdf_generator or PDFGenerator(
                output_dir=self.config.pdfs_dir,
                logo_path=self.config.logo_path,
                template_name=self.config.template_name,
                stylesheet_name=self.config.stylesheet_name,
            )
        else:
            ensure_directories()
            self.extractor = extractor or ExcelExtractor()
            self.csv_manager = csv_manager or CsvManager()
            self.spreadsheet_generator = spreadsheet_generator or SpreadsheetGenerator()
            self.pdf_generator = pdf_generator or PDFGenerator()

    def processar_upload(self, arquivo_excel: Path) -> Dict[str, Path | Certificado]:
        bundle = self.extractor.extract(Path(arquivo_excel))
        return self._persistir_bundle(bundle)

    def criar_manual(self, payload: Dict[str, object]) -> Dict[str, Path | Certificado]:
        bundle = self._bundle_from_payload(payload)
        return self._persistir_bundle(bundle)

    def exportar_certificado(self, numero_certificado: str) -> Optional[Dict[str, Path | Certificado]]:
        bundle = self.csv_manager.get_bundle_by_numero(numero_certificado)
        if not bundle:
            return None
        return self._generate_outputs(bundle, bundle.certificado)

    def listar_certificados(self) -> List[Certificado]:
        return self.csv_manager.list_certificados()

    def _persistir_bundle(self, bundle: CertificadoBundle) -> Dict[str, Path | Certificado]:
        existing = self.csv_manager.get_bundle_by_arquivo(bundle.certificado.arquivo_origem)
        
        if existing:
            planilha = self.spreadsheet_generator.consolidated_path
            
            pdf_pattern = f"*{existing.certificado.cnpj.replace('.', '').replace('/', '').replace('-', '')[:8]}*{existing.certificado.numero_certificado.replace('/', '-')}*.pdf"
            pdfs = list(self.pdf_generator.output_dir.glob(pdf_pattern))
            
            if pdfs:
                pdf = pdfs[0]
            else:
                pdf = self.pdf_generator.generate(existing)
            
            return {
                "certificado": existing.certificado,
                "planilha": planilha,
                "pdf": pdf,
            }
        
        certificado = self.csv_manager.append_bundle(bundle, skip_if_exists=True)
        return self._generate_outputs(bundle, certificado)

    def _generate_outputs(
        self, bundle: CertificadoBundle, certificado: Certificado
    ) -> Dict[str, Path | Certificado]:
        if not self.skip_validation:
            CertificadoValidator.validate_bundle(bundle)
        planilha = self.spreadsheet_generator.generate(bundle)
        pdf = self.pdf_generator.generate(bundle)
        return {
            "certificado": certificado,
            "planilha": planilha,
            "pdf": pdf,
        }

    def _bundle_from_payload(self, payload: Dict[str, object]) -> CertificadoBundle:
        if not self.skip_validation:
            CertificadoValidator.validate_payload_structure(payload)
        
        certificado_payload = payload["certificado"]
        produtos_payload = payload.get("produtos", []) or []
        metodos_payload = payload.get("metodos", []) or []

        certificado = MotorCertificados._certificado_from_dict(
            certificado_payload, payload.get("arquivo_origem", FILE_ORIGIN_MANUAL)
        )

        produtos: List[ProdutoQuimico] = []
        for item in produtos_payload:
            if not isinstance(item, dict):
                raise ValidationError(["Invalid product item"])
            produtos.append(ProdutoQuimico.from_dict(item))

        metodos: List[MetodoAplicacao] = []
        for item in metodos_payload:
            if not isinstance(item, dict):
                raise ValidationError(["Invalid method item"])
            metodos.append(MetodoAplicacao.from_dict(item))

        return CertificadoBundle(certificado=certificado, produtos=produtos, metodos=metodos)

    @staticmethod
    def _certificado_from_dict(data: Dict[str, object], arquivo_origem: str) -> Certificado:
        data_execucao = MotorCertificados._parse_date(data.get("data_execucao"))
        data_validade = MotorCertificados._parse_date(data.get("data_validade"))
        numero = data.get("numero") or data.get("numero_certificado")
        licenca = data.get("licenca") or data.get("numero_licenca")
        endereco = data.get("endereco") or data.get("endereco_completo")

        if not numero or not licenca:
            raise ValidationError(["Certificate number and license are required"])

        bairro = str(data["bairro"]) if data.get("bairro") else None
        cidade = str(data["cidade"]) if data.get("cidade") else None
        
        if (not bairro or not cidade) and endereco:
            partes = [p.strip() for p in str(endereco).split(",")]
            if len(partes) >= 3:
                if not bairro:
                    bairro = partes[-2]
                if not cidade:
                    cidade = partes[-1]

        return Certificado(
            numero_certificado=str(numero),
            numero_licenca=str(licenca),
            razao_social=str(data.get("razao_social", "")),
            nome_fantasia=str(data.get("nome_fantasia", "")),
            cnpj=str(data.get("cnpj", "")),
            endereco_completo=str(endereco or ""),
            data_execucao=data_execucao,
            data_validade=data_validade,
            pragas_tratadas=str(data.get("pragas_tratadas", "")),
            arquivo_origem=arquivo_origem,
            data_cadastro=datetime.now(timezone.utc),
            valor=str(data["valor"]) if data.get("valor") else None,
            bairro=bairro,
            cidade=cidade,
        )

    @staticmethod
    def _parse_date(value: object) -> date:
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str) and value:
            try:
                return date.fromisoformat(value)
            except ValueError as exc:
                raise ValidationError([f"Invalid date format: {value}"]) from exc
        raise ValidationError(["Execution and expiration dates are required"])
