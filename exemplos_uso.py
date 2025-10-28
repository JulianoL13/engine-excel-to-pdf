"""
Examples of using the library with batch processing and custom configuration.
"""

from pathlib import Path
from engine_excel_to_pdf import BatchProcessor, EngineConfig, MotorCertificados


def exemplo_basico():
    """Basic usage - process an entire folder with default configuration."""
    print("=== Basic Example ===\n")
    
    processor = BatchProcessor()
    
    resultados = processor.processar_pasta(
        pasta=Path("caminho/para/certificados"),
        recursivo=False,
        continuar_erro=True,
    )
    
    print(f"Total processed: {resultados['total']}")
    print(f"Successes: {len(resultados['sucessos'])}")
    print(f"Errors: {len(resultados['erros'])}")
    
    for resultado in resultados["sucessos"]:
        print(f"✓ {resultado.certificado_numero} - {resultado.arquivo.name}")
        print(f"  PDF: {resultado.pdf_path}")
        print(f"  Spreadsheet: {resultado.planilha_path}")
    
    for resultado in resultados["erros"]:
        print(f"✗ {resultado.arquivo.name}")
        print(f"  Error: {resultado.erro}")


def exemplo_paralelo():
    """Parallel processing - process multiple files simultaneously."""
    print("\n=== Parallel Processing Example ===\n")
    
    processor = BatchProcessor(max_workers=4)
    
    resultados = processor.processar_pasta(
        pasta=Path("caminho/para/certificados"),
        recursivo=True,
        continuar_erro=True,
    )
    
    print(f"Processed {resultados['total']} files using 4 parallel workers")
    print(f"✓ {len(resultados['sucessos'])} successes")
    print(f"✗ {len(resultados['erros'])} errors")


def exemplo_customizado():
    """Custom configuration for directories."""
    print("\n=== Custom Configuration Example ===\n")
    
    config = EngineConfig(
        output_dir=Path("/meu/projeto/resultados"),
        pdfs_subdir="certificados_pdf",
        planilhas_subdir="excel",
        dados_subdir="database",
        logo_path=Path("/meu/projeto/assets/logo.png"),
        sobrescrever_existentes=True,
    )
    
    motor = MotorCertificados(config=config)
    
    processor = BatchProcessor(motor=motor)
    
    resultados = processor.processar_pasta(
        pasta=Path("/entrada/certificados"),
        recursivo=True,
    )
    
    print(f"Arquivos processados: {resultados['total']}")


def exemplo_dict_config():
    """Uso com configuração via dicionário."""
    print("\n=== Exemplo com Dicionário ===\n")
    
    config_dict = {
        "output_dir": "/projeto/saidas",
        "pdfs_subdir": "pdfs",
        "planilhas_subdir": "planilhas",
        "dados_subdir": "dados",
        "logo_path": "/projeto/logo.png",
        "template_name": "certificado.html",
        "sobrescrever_existentes": False,
    }
    
    config = EngineConfig.from_dict(config_dict)
    motor = MotorCertificados(config=config)
    processor = BatchProcessor(motor=motor)
    
    resultados = processor.processar_pasta(Path("/entrada"))
    
    print(f"Processados: {resultados['total']}")


def exemplo_arquivo_unico():
    """Processar um único arquivo com saída customizada."""
    print("\n=== Exemplo Arquivo Único ===\n")
    
    config = EngineConfig(
        output_dir=Path("./resultados_cliente_x"),
        pdfs_subdir="pdfs",
        planilhas_subdir="planilhas",
    )
    
    motor = MotorCertificados(config=config)
    
    resultado = motor.processar_upload(Path("certificado_cliente.xlsx"))
    
    print(f"Certificado: {resultado['certificado'].numero_certificado}")
    print(f"PDF salvo em: {resultado['pdf']}")
    print(f"Planilha salva em: {resultado['planilha']}")


def exemplo_variaveis_ambiente():
    """Uso com variáveis de ambiente (útil para containers/deploy)."""
    print("\n=== Exemplo com Variáveis de Ambiente ===\n")
    
    import os
    
    os.environ["ENGINE_STORAGE_ROOT"] = "/app/dados"
    os.environ["ENGINE_ASSETS_DIR"] = "/app/assets"
    
    motor = MotorCertificados()
    
    config = EngineConfig(
        output_dir=Path(os.getenv("OUTPUT_DIR", "./resultados")),
        logo_path=Path(os.getenv("LOGO_PATH", "./logo.png")),
    )
    motor_custom = MotorCertificados(config=config)


if __name__ == "__main__":
    print("Executando exemplos de uso...\n")
    
    print("\nVerifique o código para ver os exemplos disponíveis!")
