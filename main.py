from __future__ import annotations

import argparse
from pathlib import Path

from engine_excel_to_pdf import BatchProcessor, CertificateEngine, EngineConfig, ValidationError


def processar_arquivo_unico(arquivo: Path, config: EngineConfig | None = None, skip_validation: bool = False) -> None:
    engine = CertificateEngine(config=config, skip_validation=skip_validation)
    
    try:
        resultado = engine.processar_upload(arquivo)
        certificado = resultado["certificado"]
        
        print(f"✓ Certificado processado: {certificado.numero_certificado}")
        print(f"  Cliente: {certificado.razao_social}")
        print(f"  PDF: {resultado['pdf']}")
        print(f"  Planilha: {resultado['planilha']}")
        
    except FileNotFoundError:
        print(f"✗ Arquivo não encontrado: {arquivo}")
    except ValidationError as exc:
        print(f"✗ Falha de validação:")
        for erro in exc.errors:
            print(f"  - {erro}")
    except Exception as e:
        print(f"✗ Erro: {e}")


def processar_lote(
    pasta: Path,
    recursivo: bool = False,
    paralelo: int | None = None,
    config: EngineConfig | None = None,
    skip_validation: bool = False,
) -> None:
    engine = CertificateEngine(config=config, skip_validation=skip_validation)
    processor = BatchProcessor(motor=engine, max_workers=paralelo)
    
    print(f"🚀 Processando pasta: {pasta}")
    print(f"   Modo: {'paralelo (' + str(paralelo) + ' workers)' if paralelo else 'sequencial'}")
    print(f"   Subpastas: {'sim' if recursivo else 'não'}")
    print()
    
    resultados = processor.processar_pasta(
        pasta=pasta,
        recursivo=recursivo,
        continuar_erro=True,
    )
    
    print(f"\n📊 Resultados:")
    print(f"   Total: {resultados['total']} arquivos")
    print(f"   ✓ Sucessos: {len(resultados['sucessos'])}")
    print(f"   ✗ Erros: {len(resultados['erros'])}")
    
    if resultados['sucessos']:
        print(f"\n✅ Processados com sucesso:")
        for r in resultados['sucessos']:
            print(f"   ✓ {r.arquivo.name} → {r.certificado_numero}")
    
    if resultados['erros']:
        print(f"\n❌ Erros:")
        for r in resultados['erros']:
            print(f"   ✗ {r.arquivo.name}: {r.erro}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Processa certificados de controle de pragas a partir de Excel.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py arquivo.xlsx
  
  python main.py --pasta ./certificados
  
  python main.py --pasta ./certificados --recursivo --paralelo 4
  
  python main.py --pasta ./certificados --output ./resultados
        """,
    )
    
    parser.add_argument(
        "arquivo",
        type=Path,
        nargs="?",
        help="Arquivo Excel único para processar",
    )
    
    parser.add_argument(
        "--pasta",
        type=Path,
        help="Pasta com múltiplos arquivos Excel",
    )
    
    parser.add_argument(
        "--recursivo",
        "-r",
        action="store_true",
        help="Processar subpastas recursivamente",
    )
    
    parser.add_argument(
        "--paralelo",
        "-p",
        type=int,
        metavar="N",
        help="Número de workers para processamento paralelo (ex: 4)",
    )
    
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Diretório de saída customizado (padrão: ./results)",
    )
    
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Pular validações (aceita qualquer dado)",
    )
    
    args = parser.parse_args()
    
    if not args.arquivo and not args.pasta:
        parser.print_help()
        return
    
    config = None
    if args.output:
        config = EngineConfig(output_dir=args.output)
    
    if args.pasta:
        processar_lote(
            pasta=args.pasta,
            recursivo=args.recursivo,
            paralelo=args.paralelo,
            config=config,
            skip_validation=args.skip_validation,
        )
    elif args.arquivo:
        processar_arquivo_unico(args.arquivo, config=config, skip_validation=args.skip_validation)


if __name__ == "__main__":
    main()
