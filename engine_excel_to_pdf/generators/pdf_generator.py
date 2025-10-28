from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

if TYPE_CHECKING:
    from weasyprint import CSS, HTML

from ..models import Certificado, CertificadoBundle, MetodoAplicacao, ProdutoQuimico
from ..config_defaults import DEFAULT_LOGO_PATH, PDFS_DIR, TEMPLATES_DIR, ensure_directories
from ..utils import normalize_whitespace, generate_unique_filename
from ..constants import DEFAULT_PLACEHOLDER


def _normalize(value: object, default: str = "") -> str:
    if value is None:
        return default
    text = normalize_whitespace(str(value))
    return text if text else default


class PDFGenerator:
    def __init__(
        self,
        output_dir: Path = PDFS_DIR,
        logo_path: Path | None = None,
        template_name: str = "certificado.html",
        stylesheet_name: str | None = "certificado.css",
    ) -> None:
        ensure_directories()
        self.output_dir = output_dir
        self.logo_path = logo_path or DEFAULT_LOGO_PATH
        self.template_name = template_name
        self.stylesheet_name = stylesheet_name
        self._environment = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        try:
            self._template = self._environment.get_template(self.template_name)
        except TemplateNotFound as exc:
            raise FileNotFoundError(
                f"HTML template '{self.template_name}' not found in {TEMPLATES_DIR}."
            ) from exc

    def generate(self, bundle: CertificadoBundle) -> Path:
        from weasyprint import CSS, HTML
        
        context = self._build_context(bundle)
        html_content = self._template.render(context)
        output_path = self.output_dir / generate_unique_filename(bundle.certificado, extensao=".pdf")

        html_document = HTML(string=html_content, base_url=str(TEMPLATES_DIR))
        stylesheets: List[CSS] = []
        if self.stylesheet_name:
            stylesheet_path = TEMPLATES_DIR / self.stylesheet_name
            if stylesheet_path.exists():
                stylesheets.append(CSS(filename=str(stylesheet_path)))

        html_document.write_pdf(str(output_path), stylesheets=stylesheets)
        return output_path

    def _build_certificate_meta(self, certificado: Certificado) -> List[Dict[str, str]]:
        return [
            {"label": "Nº Certificado", "value": _normalize(certificado.numero_certificado)},
            {"label": "Nº Licença", "value": _normalize(certificado.numero_licenca)},
            {"label": "Execução", "value": certificado.data_execucao.strftime("%d/%m/%Y")},
            {"label": "Validade", "value": certificado.data_validade.strftime("%d/%m/%Y")},
            {"label": "Processado", "value": certificado.data_cadastro.strftime("%d/%m/%Y %H:%M:%S")},
        ]

    def _build_client_rows(self, certificado: Certificado, placeholder: str) -> List[Dict[str, str]]:
        return [
            {
                "label": "Razão Social",
                "value": _normalize(certificado.razao_social, placeholder),
                "extra": _normalize(certificado.pragas_tratadas, placeholder),
            },
            {
                "label": "Nome Fantasia",
                "value": _normalize(certificado.nome_fantasia, placeholder),
                "extra": placeholder,
            },
            {
                "label": "Endereço",
                "value": _normalize(certificado.endereco_completo, placeholder),
                "extra": placeholder,
            },
        ]

    def _build_schedule_rows(self, certificado: Certificado, placeholder: str) -> List[Dict[str, str]]:
        rows = [
            {
                "label": "Data de Execução",
                "value": certificado.data_execucao.strftime("%d/%m/%Y"),
                "extra": placeholder,
            },
            {
                "label": "Data de Validade",
                "value": certificado.data_validade.strftime("%d/%m/%Y"),
                "extra": placeholder,
            },
        ]
        
        if certificado.valor:
            rows.append({
                "label": "Valor",
                "value": _normalize(certificado.valor, placeholder),
                "extra": placeholder,
            })
        
        return rows

    def _build_products_list(self, produtos: List[ProdutoQuimico], placeholder: str) -> List[Dict[str, str]]:
        return [
            {
                "nome": _normalize(produto.nome_produto, placeholder),
                "classe": _normalize(produto.classe_quimica, placeholder),
                "concentracao": (
                    placeholder
                    if produto.concentracao is None
                    else f"{produto.concentracao * 100:g}%"
                ),
            }
            for produto in produtos
        ]

    def _build_methods_list(self, metodos: List[MetodoAplicacao], placeholder: str) -> List[Dict[str, str]]:
        return [
            {
                "nome": _normalize(metodo.metodo, placeholder),
                "quantidade": _normalize(metodo.quantidade, placeholder),
            }
            for metodo in metodos
        ]

    def _build_process_info(self, certificado: Certificado, placeholder: str) -> List[Dict[str, str]]:
        return [
            {"label": "Arquivo de origem", "value": _normalize(certificado.arquivo_origem, placeholder)},
            {"label": "Gerado em", "value": certificado.data_cadastro.strftime("%d/%m/%Y %H:%M:%S")},
        ]

    def _build_context(self, bundle: CertificadoBundle) -> Dict[str, Any]:
        certificado = bundle.certificado
        placeholder = DEFAULT_PLACEHOLDER
        logo_url = None
        if self.logo_path and Path(self.logo_path).exists():
            logo_url = Path(self.logo_path).resolve().as_uri()

        context: Dict[str, Any] = {
            "certificate": {
                "numero_certificado": _normalize(certificado.numero_certificado),
                "razao_social": _normalize(certificado.razao_social),
                "nome_fantasia": _normalize(certificado.nome_fantasia),
                "cnpj": _normalize(certificado.cnpj),
                "endereco": _normalize(certificado.endereco_completo),
                "pragas": _normalize(certificado.pragas_tratadas, placeholder),
                "bairro": _normalize(certificado.bairro, placeholder),
                "cidade": _normalize(certificado.cidade, placeholder),
            },
            "certificate_meta": self._build_certificate_meta(certificado),
            "cliente_rows": self._build_client_rows(certificado, placeholder),
            "prazos_rows": self._build_schedule_rows(certificado, placeholder),
            "produtos": self._build_products_list(bundle.produtos, placeholder),
            "metodos": self._build_methods_list(bundle.metodos, placeholder),
            "process_info": self._build_process_info(certificado, placeholder),
            "placeholder": placeholder,
            "logo_url": logo_url,
        }

        return context
