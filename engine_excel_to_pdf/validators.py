from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, TypeVar

from .models import Certificado, CertificadoBundle, MetodoAplicacao, ProdutoQuimico
from .utils import extract_cnpj, normalize_whitespace

T = TypeVar('T')


class ValidationError(Exception):
    def __init__(self, errors: List[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


class CertificadoValidator:
    REQUIRED_FIELDS = (
        "numero_certificado",
        "numero_licenca",
        "razao_social",
        "nome_fantasia",
        "cnpj",
        "endereco_completo",
        "data_execucao",
        "data_validade",
        "pragas_tratadas",
    )
    
    NORMALIZABLE_FIELDS = (
        "razao_social",
        "nome_fantasia",
        "endereco_completo",
        "pragas_tratadas",
    )

    @staticmethod
    def validate_payload_structure(payload: Dict[str, Any]) -> None:
        """Validate the structure of a manual entry payload.
        
        Args:
            payload: Dictionary containing certificado, produtos, and metodos
            
        Raises:
            ValidationError: If structure is invalid
        """
        errors: List[str] = []
        
        certificado_payload = payload.get("certificado")
        if not isinstance(certificado_payload, dict):
            errors.append("'certificado' structure missing or invalid")
        
        produtos_payload = payload.get("produtos")
        if produtos_payload is None:
            produtos_payload = []
        if not isinstance(produtos_payload, list):
            errors.append("'produtos' structure invalid - must be a list")
        
        metodos_payload = payload.get("metodos")
        if metodos_payload is None:
            metodos_payload = []
        if not isinstance(metodos_payload, list):
            errors.append("'metodos' structure invalid - must be a list")
        
        if errors:
            raise ValidationError(errors)

    @classmethod
    def validate_certificado(cls, certificado: Certificado) -> None:
        errors: List[str] = []

        for field_name in cls.REQUIRED_FIELDS:
            if not getattr(certificado, field_name):
                errors.append(f"Required field missing: {field_name}")

        if certificado.data_validade < certificado.data_execucao:
            errors.append("Expiration date is before execution date")

        cnpj = extract_cnpj(certificado.cnpj)
        if not cnpj:
            errors.append("Invalid or missing CNPJ")
        else:
            certificado.cnpj = cnpj

        for field_name in cls.NORMALIZABLE_FIELDS:
            value = getattr(certificado, field_name)
            setattr(certificado, field_name, normalize_whitespace(value))

        if errors:
            raise ValidationError(errors)

    @classmethod
    def _validate_items(
        cls,
        items: Iterable[T],
        item_name: str,
        validators: List[Callable[[T], List[str]]]
    ) -> None:
        """Generic method to validate collections of items."""
        errors: List[str] = []
        for index, item in enumerate(items, start=1):
            for validator in validators:
                item_errors = validator(item)
                errors.extend([f"{item_name} {index}: {err}" for err in item_errors])
        if errors:
            raise ValidationError(errors)

    @classmethod
    def validate_produtos(cls, produtos: Iterable[ProdutoQuimico]) -> None:
        def validate_produto(produto: ProdutoQuimico) -> List[str]:
            errors = []
            if not produto.nome_produto:
                errors.append("missing product name")
            if not produto.classe_quimica:
                errors.append("missing chemical class")
            return errors
        
        cls._validate_items(produtos, "Product", [validate_produto])

    @classmethod
    def validate_metodos(cls, metodos: Iterable[MetodoAplicacao]) -> None:
        def validate_metodo(metodo: MetodoAplicacao) -> List[str]:
            errors = []
            if not metodo.metodo:
                errors.append("missing method description")
            if not metodo.quantidade:
                errors.append("missing quantity")
            return errors
        
        cls._validate_items(metodos, "Method", [validate_metodo])

    @classmethod
    def validate_bundle(cls, bundle: CertificadoBundle) -> None:
        cls.validate_certificado(bundle.certificado)
        cls.validate_produtos(bundle.produtos)
        cls.validate_metodos(bundle.metodos)
