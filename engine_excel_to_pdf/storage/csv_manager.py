from __future__ import annotations

import csv
from contextlib import ExitStack
from datetime import datetime, date
from pathlib import Path
from typing import Callable, Iterable, List, Optional, TypeVar

from ..models import Certificado, CertificadoBundle, MetodoAplicacao, ProdutoQuimico
from ..config_defaults import DATA_DIR
from ..constants import CSV_CERTIFICATES, CSV_PRODUCTS, CSV_METHODS

T = TypeVar('T')

CERTIFICADOS_HEADERS = [
    "id",
    "numero_certificado",
    "numero_licenca",
    "razao_social",
    "nome_fantasia",
    "cnpj",
    "endereco_completo",
    "data_execucao",
    "data_validade",
    "pragas_tratadas",
    "arquivo_origem",
    "data_cadastro",
    "valor",
    "bairro",
    "cidade",
]

PRODUTOS_HEADERS = [
    "id",
    "id_certificado",
    "numero_certificado",
    "nome_produto",
    "classe_quimica",
    "concentracao",
]

METODOS_HEADERS = [
    "id",
    "id_certificado",
    "numero_certificado",
    "metodo",
    "quantidade",
]


class CsvManager:
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.certificados_path = self.data_dir / CSV_CERTIFICATES
        self.produtos_path = self.data_dir / CSV_PRODUCTS
        self.metodos_path = self.data_dir / CSV_METHODS
        self._ensure_headers()

    def _ensure_headers(self) -> None:
        self._ensure_file(self.certificados_path, CERTIFICADOS_HEADERS)
        self._ensure_file(self.produtos_path, PRODUTOS_HEADERS)
        self._ensure_file(self.metodos_path, METODOS_HEADERS)

    @staticmethod
    def _ensure_file(path: Path, headers: Iterable[str]) -> None:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=headers)
                writer.writeheader()

    def append_bundle(self, bundle: CertificadoBundle, skip_if_exists: bool = True) -> Certificado:
        if skip_if_exists:
            existing = self.get_bundle_by_arquivo(bundle.certificado.arquivo_origem)
            if existing:
                return existing.certificado
        
        if bundle.certificado.id is None:
            bundle.certificado.id = bundle.certificado._generate_id()
        
        certificado_id = bundle.certificado.id
        
        with ExitStack() as stack:
            cert_file = stack.enter_context(
                self.certificados_path.open("a", newline="", encoding="utf-8")
            )
            prod_file = stack.enter_context(
                self.produtos_path.open("a", newline="", encoding="utf-8")
            )
            met_file = stack.enter_context(
                self.metodos_path.open("a", newline="", encoding="utf-8")
            )
            
            cert_writer = csv.DictWriter(cert_file, fieldnames=CERTIFICADOS_HEADERS)
            cert_row = {
                "id": certificado_id,
                "numero_certificado": bundle.certificado.numero_certificado,
                "numero_licenca": bundle.certificado.numero_licenca,
                "razao_social": bundle.certificado.razao_social,
                "nome_fantasia": bundle.certificado.nome_fantasia,
                "cnpj": bundle.certificado.cnpj,
                "endereco_completo": bundle.certificado.endereco_completo,
                "data_execucao": bundle.certificado.data_execucao.isoformat(),
                "data_validade": bundle.certificado.data_validade.isoformat(),
                "pragas_tratadas": bundle.certificado.pragas_tratadas,
                "arquivo_origem": bundle.certificado.arquivo_origem,
                "data_cadastro": bundle.certificado.data_cadastro.isoformat(),
                "valor": bundle.certificado.valor or "",
                "bairro": bundle.certificado.bairro or "",
                "cidade": bundle.certificado.cidade or "",
            }
            cert_writer.writerow(cert_row)
            
            prod_writer = csv.DictWriter(prod_file, fieldnames=PRODUTOS_HEADERS)
            for idx, produto in enumerate(bundle.produtos, start=1):
                prod_row = {
                    "id": f"{certificado_id}-P{idx:03d}",
                    "id_certificado": certificado_id,
                    "numero_certificado": bundle.certificado.numero_certificado,
                    "nome_produto": produto.nome_produto,
                    "classe_quimica": produto.classe_quimica,
                    "concentracao": "" if produto.concentracao is None else str(produto.concentracao),
                }
                prod_writer.writerow(prod_row)
            
            met_writer = csv.DictWriter(met_file, fieldnames=METODOS_HEADERS)
            for idx, metodo in enumerate(bundle.metodos, start=1):
                met_row = {
                    "id": f"{certificado_id}-M{idx:03d}",
                    "id_certificado": certificado_id,
                    "numero_certificado": bundle.certificado.numero_certificado,
                    "metodo": metodo.metodo,
                    "quantidade": metodo.quantidade,
                }
                met_writer.writerow(met_row)
        
        return bundle.certificado

    def _append_certificado(self, certificado: Certificado) -> None:
        row = {
            "id": certificado.id,
            "numero_certificado": certificado.numero_certificado,
            "numero_licenca": certificado.numero_licenca,
            "razao_social": certificado.razao_social,
            "nome_fantasia": certificado.nome_fantasia,
            "cnpj": certificado.cnpj,
            "endereco_completo": certificado.endereco_completo,
            "data_execucao": certificado.data_execucao.isoformat(),
            "data_validade": certificado.data_validade.isoformat(),
            "pragas_tratadas": certificado.pragas_tratadas,
            "arquivo_origem": certificado.arquivo_origem,
            "data_cadastro": certificado.data_cadastro.isoformat(),
            "valor": certificado.valor or "",
            "bairro": certificado.bairro or "",
            "cidade": certificado.cidade or "",
        }
        with self.certificados_path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=CERTIFICADOS_HEADERS)
            writer.writerow(row)

    def _append_items(
        self,
        path: Path,
        headers: List[str],
        certificado_id: str,
        numero_certificado: str,
        items: Iterable[T],
        map_fn: Callable[[str, str, str, T], dict]
    ) -> None:
        with path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            for idx, item in enumerate(items, start=1):
                item_id = f"{certificado_id}-{idx:03d}"
                row = map_fn(item_id, certificado_id, numero_certificado, item)
                writer.writerow(row)

    def _append_produtos(self, certificado_id: str, numero_certificado: str, produtos: Iterable[ProdutoQuimico]) -> None:
        def map_produto(item_id: str, cert_id: str, cert_numero: str, produto: ProdutoQuimico) -> dict:
            return {
                "id": item_id,
                "id_certificado": cert_id,
                "numero_certificado": cert_numero,
                "nome_produto": produto.nome_produto,
                "classe_quimica": produto.classe_quimica,
                "concentracao": "" if produto.concentracao is None else str(produto.concentracao),
            }
        self._append_items(self.produtos_path, PRODUTOS_HEADERS, certificado_id, numero_certificado, produtos, map_produto)

    def _append_metodos(self, certificado_id: str, numero_certificado: str, metodos: Iterable[MetodoAplicacao]) -> None:
        def map_metodo(item_id: str, cert_id: str, cert_numero: str, metodo: MetodoAplicacao) -> dict:
            return {
                "id": item_id,
                "id_certificado": cert_id,
                "numero_certificado": cert_numero,
                "metodo": metodo.metodo,
                "quantidade": metodo.quantidade,
            }
        self._append_items(self.metodos_path, METODOS_HEADERS, certificado_id, numero_certificado, metodos, map_metodo)

    def get_bundle_by_numero(self, numero_certificado: str) -> Optional[CertificadoBundle]:
        certificado = self._load_certificado(numero_certificado)
        if not certificado:
            return None
        produtos = self._load_produtos(certificado.id)
        metodos = self._load_metodos(certificado.id)
        return CertificadoBundle(certificado=certificado, produtos=produtos, metodos=metodos)
    
    def get_bundle_by_arquivo(self, arquivo_origem: str) -> Optional[CertificadoBundle]:
        certificado = self._load_certificado_by_arquivo(arquivo_origem)
        if not certificado:
            return None
        produtos = self._load_produtos(certificado.id)
        metodos = self._load_metodos(certificado.id)
        return CertificadoBundle(certificado=certificado, produtos=produtos, metodos=metodos)

    def list_certificados(self) -> List[Certificado]:
        certificados: List[Certificado] = []
        if not self.certificados_path.exists():
            return certificados
        with self.certificados_path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                certificados.append(self._row_to_certificado(row))
        return certificados

    def _load_certificado(self, numero_certificado: str) -> Optional[Certificado]:
        if not self.certificados_path.exists():
            return None
        with self.certificados_path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if row["numero_certificado"] == numero_certificado:
                    return self._row_to_certificado(row)
        return None
    
    def _load_certificado_by_arquivo(self, arquivo_origem: str) -> Optional[Certificado]:
        if not self.certificados_path.exists():
            return None
        with self.certificados_path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if row["arquivo_origem"] == arquivo_origem:
                    return self._row_to_certificado(row)
        return None

    def _load_items(
        self,
        path: Path,
        certificado_id: Optional[str],
        map_fn: Callable[[dict], T]
    ) -> List[T]:
        items: List[T] = []
        if not path.exists() or certificado_id is None:
            return items
        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if row["id_certificado"] == certificado_id:
                    items.append(map_fn(row))
        return items

    def _load_produtos(self, certificado_id: Optional[str]) -> List[ProdutoQuimico]:
        def map_produto(row: dict) -> ProdutoQuimico:
            return ProdutoQuimico(
                nome_produto=row["nome_produto"],
                classe_quimica=row["classe_quimica"],
                concentracao=float(row["concentracao"]) if row["concentracao"] else None,
            )
        return self._load_items(self.produtos_path, certificado_id, map_produto)

    def _load_metodos(self, certificado_id: Optional[str]) -> List[MetodoAplicacao]:
        def map_metodo(row: dict) -> MetodoAplicacao:
            return MetodoAplicacao(
                metodo=row["metodo"],
                quantidade=row["quantidade"],
            )
        return self._load_items(self.metodos_path, certificado_id, map_metodo)

    @staticmethod
    def _row_to_certificado(row: dict[str, str]) -> Certificado:
        return Certificado(
            id=row["id"],
            numero_certificado=row["numero_certificado"],
            numero_licenca=row["numero_licenca"],
            razao_social=row["razao_social"],
            nome_fantasia=row["nome_fantasia"],
            cnpj=row["cnpj"],
            endereco_completo=row["endereco_completo"],
            data_execucao=date.fromisoformat(row["data_execucao"]),
            data_validade=date.fromisoformat(row["data_validade"]),
            pragas_tratadas=row["pragas_tratadas"],
            arquivo_origem=row["arquivo_origem"],
            data_cadastro=datetime.fromisoformat(row["data_cadastro"]),
            valor=row.get("valor") or None,
            bairro=row.get("bairro") or None,
            cidade=row.get("cidade") or None,
        )
