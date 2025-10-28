from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class ProdutoQuimico:
    nome_produto: str
    classe_quimica: str
    concentracao: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProdutoQuimico":
        concentracao_value = data.get("concentracao")
        concentracao = None
        if concentracao_value not in (None, ""):
            try:
                concentracao = float(str(concentracao_value).replace(",", "."))
            except ValueError:
                concentracao = None
        
        return cls(
            nome_produto=str(data.get("nome") or data.get("nome_produto", "")),
            classe_quimica=str(data.get("classe") or data.get("classe_quimica", "")),
            concentracao=concentracao,
        )


@dataclass(slots=True)
class MetodoAplicacao:
    metodo: str
    quantidade: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetodoAplicacao":
        return cls(
            metodo=str(data.get("descricao") or data.get("metodo", "")),
            quantidade=str(data.get("quantidade", "")),
        )


@dataclass(slots=True)
class Certificado:
    numero_certificado: str
    numero_licenca: str
    razao_social: str
    nome_fantasia: str
    cnpj: str
    endereco_completo: str
    data_execucao: date
    data_validade: date
    pragas_tratadas: str
    arquivo_origem: str
    data_cadastro: datetime
    id: Optional[str] = field(default=None)
    valor: Optional[str] = field(default=None)
    bairro: Optional[str] = field(default=None)
    cidade: Optional[str] = field(default=None)

    def __post_init__(self):
        if self.id is None:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        data_str = (
            f"{self.cnpj}|"
            f"{self.numero_certificado}|"
            f"{self.data_cadastro.isoformat()}"
        )
        hash_obj = hashlib.sha256(data_str.encode('utf-8'))
        return hash_obj.hexdigest()[:12]

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["data_execucao"] = self.data_execucao.isoformat()
        payload["data_validade"] = self.data_validade.isoformat()
        payload["data_cadastro"] = self.data_cadastro.isoformat()
        return payload


@dataclass(slots=True)
class CertificadoBundle:
    certificado: Certificado
    produtos: List[ProdutoQuimico]
    metodos: List[MetodoAplicacao]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certificado": self.certificado.to_dict(),
            "produtos": [produto.to_dict() for produto in self.produtos],
            "metodos": [metodo.to_dict() for metodo in self.metodos],
        }
