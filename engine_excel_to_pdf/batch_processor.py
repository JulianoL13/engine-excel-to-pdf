from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional

from .interface import MotorCertificados
from .validators import ValidationError

logger = logging.getLogger(__name__)


class ProcessingResult:

    def __init__(
        self,
        arquivo: Path,
        sucesso: bool,
        certificado_numero: Optional[str] = None,
        pdf_path: Optional[Path] = None,
        planilha_path: Optional[Path] = None,
        erro: Optional[str] = None,
    ):
        self.arquivo = arquivo
        self.sucesso = sucesso
        self.certificado_numero = certificado_numero
        self.pdf_path = pdf_path
        self.planilha_path = planilha_path
        self.erro = erro

    def __repr__(self) -> str:
        status = "✓" if self.sucesso else "✗"
        return f"ProcessingResult({status} {self.arquivo.name})"


class BatchProcessor:

    def __init__(
        self,
        motor: Optional[MotorCertificados] = None,
        extensoes: Optional[List[str]] = None,
        max_workers: Optional[int] = None,
        skip_validation: bool = False,
    ):
        """
        Initialize batch processor.
        
        Args:
            motor: Certificate engine instance (creates default if None)
            extensoes: File extensions to process (default: ['.xlsx', '.xls'])
            max_workers: Number of parallel workers (None = sequential)
            skip_validation: Skip validation checks if True
        """
        self.motor = motor or MotorCertificados(skip_validation=skip_validation)
        self.extensoes = extensoes or [".xlsx", ".xls"]
        self.max_workers = max_workers

    def processar_pasta(
        self,
        pasta: Path,
        recursivo: bool = False,
        continuar_erro: bool = True,
    ) -> Dict[str, List[ProcessingResult]]:
        """
        Process all Excel files in a folder.

        Args:
            pasta: Directory containing files
            recursivo: Whether to process subdirectories
            continuar_erro: Whether to continue processing after errors

        Returns:
            Dict with 'sucessos' and 'erros' containing ProcessingResult lists
        """
        pasta = Path(pasta)
        if not pasta.exists():
            raise FileNotFoundError(f"Folder not found: {pasta}")

        if not pasta.is_dir():
            raise ValueError(f"Path is not a directory: {pasta}")

        arquivos = self._listar_arquivos(pasta, recursivo)
        logger.info(f"Found {len(arquivos)} files to process")

        if self.max_workers and self.max_workers > 0:
            resultados = self._processar_paralelo(arquivos, continuar_erro)
        else:
            resultados = self._processar_sequencial(arquivos, continuar_erro)

        sucessos = [r for r in resultados if r.sucesso]
        erros = [r for r in resultados if not r.sucesso]

        logger.info(f"Processing completed: {len(sucessos)} successes, {len(erros)} errors")

        return {
            "sucessos": sucessos,
            "erros": erros,
            "total": len(resultados),
        }

    def _processar_sequencial(
        self, arquivos: List[Path], continuar_erro: bool
    ) -> List[ProcessingResult]:
        resultados: List[ProcessingResult] = []

        for arquivo in arquivos:
            resultado = self._processar_arquivo(arquivo)
            resultados.append(resultado)

            if not resultado.sucesso and not continuar_erro:
                logger.error(f"Stopping processing due to error in {arquivo.name}")
                break

        return resultados

    def _processar_paralelo(
        self, arquivos: List[Path], continuar_erro: bool
    ) -> List[ProcessingResult]:
        """Process files in parallel using ThreadPoolExecutor.
        
        Note: Uses threads (not processes) since PDF/Excel generation is I/O-bound.
        WeasyPrint and openpyxl spend most time waiting on file I/O and rendering.
        """
        resultados: List[ProcessingResult] = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_arquivo = {
                executor.submit(self._processar_arquivo, arquivo): arquivo
                for arquivo in arquivos
            }
            
            for future in as_completed(future_to_arquivo):
                arquivo = future_to_arquivo[future]
                try:
                    resultado = future.result()
                    resultados.append(resultado)
                    
                    if not resultado.sucesso and not continuar_erro:
                        logger.error(f"Stopping processing due to error in {arquivo.name}")
                        for f in future_to_arquivo:
                            f.cancel()
                        break
                        
                except Exception as e:
                    logger.error(f"Unexpected error processing {arquivo.name}: {e}", exc_info=True)
                    resultados.append(
                        ProcessingResult(arquivo=arquivo, sucesso=False, erro=str(e))
                    )
        
        return resultados

    def _listar_arquivos(self, pasta: Path, recursivo: bool) -> List[Path]:
        arquivos: List[Path] = []

        if recursivo:
            for ext in self.extensoes:
                arquivos.extend(pasta.rglob(f"*{ext}"))
        else:
            for ext in self.extensoes:
                arquivos.extend(pasta.glob(f"*{ext}"))

        return sorted(arquivos)

    def _processar_arquivo(self, arquivo: Path) -> ProcessingResult:
        try:
            logger.info(f"Processando: {arquivo.name}")
            resultado = self.motor.processar_upload(arquivo)

            return ProcessingResult(
                arquivo=arquivo,
                sucesso=True,
                certificado_numero=resultado["certificado"].numero_certificado,
                pdf_path=resultado["pdf"],
                planilha_path=resultado["planilha"],
            )

        except ValidationError as e:
            logger.warning(f"Erro de validação em {arquivo.name}: {e.errors}")
            return ProcessingResult(
                arquivo=arquivo,
                sucesso=False,
                erro=f"Validação: {', '.join(e.errors)}",
            )

        except Exception as e:
            logger.error(f"Erro ao processar {arquivo.name}: {e}", exc_info=True)
            return ProcessingResult(
                arquivo=arquivo,
                sucesso=False,
                erro=str(e),
            )
