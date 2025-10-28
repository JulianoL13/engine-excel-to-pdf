# Engine Excel to PDF

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-71%20passed-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-84.7%25-brightgreen.svg)](htmlcov/)

Motor Python para extração, validação e geração de certificados de controle de pragas a partir de planilhas Excel.

## ✨ Características

- 📂 **Extração automática** de dados de planilhas Excel desestruturadas
- ✅ **Validação completa** de campos obrigatórios e CNPJ (com checksum)
- 📊 **Geração de planilhas** consolidadas em Excel com dados estruturados
- 🎨 **Geração de PDFs** profissionais com templates HTML/CSS customizáveis
- 💾 **Persistência em CSV** com ID único baseado em hash
- 🚀 **Processamento em lote** sequencial ou paralelo (ThreadPoolExecutor)
- ⚙️ **Configuração flexível** de diretórios de saída e templates
- 🔄 **Campos opcionais** suportados: valor, bairro e cidade
- 🚫 **Skip validation mode** para cenários de confiança total
- 🧪 **84.7% de cobertura** de testes automatizados

---

## 🚀 Instalação

### Como biblioteca

```bash
# Via pip (quando publicado no PyPI)
pip install engine-excel-to-pdf

# Via git (desenvolvimento)
pip install git+https://github.com/JulianoL13/engine-excel-to-pdf.git

# Instalação local para desenvolvimento
pip install -e .
```

### Para desenvolvimento

```bash
git clone https://github.com/JulianoL13/engine-excel-to-pdf.git
cd engine-excel-to-pdf

# Com uv (recomendado)
uv sync --extra dev

# Ou com pip
pip install -e ".[dev]"
```

---

## 📖 Uso Básico

### Processar arquivo Excel

```python
from pathlib import Path
from engine_excel_to_pdf import CertificateEngine

engine = CertificateEngine()
resultado = engine.processar_upload(Path("certificado.xlsx"))

print(f"✓ Certificado: {resultado['certificado'].numero_certificado}")
print(f"  PDF: {resultado['pdf']}")
print(f"  Planilha: {resultado['planilha']}")
```

### Criar certificado manualmente

```python
from engine_excel_to_pdf import CertificateEngine

engine = CertificateEngine()

payload = {
    "certificado": {
        "numero_certificado": "001/2025",
        "numero_licenca": "LIC-123",
        "razao_social": "Empresa Exemplo LTDA",
        "nome_fantasia": "Exemplo Store",
        "cnpj": "11.222.333/0001-81",
        "endereco_completo": "Rua Exemplo, 123, Centro, São Paulo/SP",
        "data_execucao": "2025-01-15",
        "data_validade": "2025-04-15",
        "pragas_tratadas": "Insetos e roedores",
        "valor": "R$ 1.500,00",  # Opcional
        "bairro": "Centro",       # Opcional (extraído automaticamente do endereço)
        "cidade": "São Paulo/SP", # Opcional (extraído automaticamente do endereço)
    },
    "produtos": [
        {
            "nome": "Inseticida Alpha",
            "classe": "Piretroide",
            "concentracao": 0.025,  # 2.5%
        }
    ],
    "metodos": [
        {
            "descricao": "Pulverização",
            "quantidade": "500ml",
        }
    ],
}

resultado = engine.criar_manual(payload)
print(f"✓ PDF: {resultado['pdf']}")
print(f"✓ Planilha: {resultado['planilha']}")
```

### Skip Validation (aceitar qualquer dado)

```python
from engine_excel_to_pdf import CertificateEngine

# Desabilita validações - útil quando dados vêm de fonte confiável
engine = CertificateEngine(skip_validation=True)

# Aceita CNPJ inválido, campos vazios, etc.
resultado = engine.criar_manual(payload_com_dados_invalidos)
```

### Processamento em lote

```python
from pathlib import Path
from engine_excel_to_pdf import BatchProcessor

# Processamento sequencial (padrão)
processor = BatchProcessor()

# Processamento paralelo (4 workers)
processor = BatchProcessor(max_workers=4)

resultados = processor.processar_pasta(
    pasta=Path("./certificados"),
    recursivo=True,      # Processa subpastas
    continuar_erro=True, # Continua mesmo com erros
)

print(f"Total: {resultados['total']}")
print(f"✓ Sucessos: {len(resultados['sucessos'])}")
print(f"✗ Erros: {len(resultados['erros'])}")

# Detalhes dos erros
for erro in resultados['erros']:
    print(f"  {erro.arquivo.name}: {erro.erro}")
```

### Configuração customizada

```python
from pathlib import Path
from engine_excel_to_pdf import EngineConfig, CertificateEngine

config = EngineConfig(
    output_dir=Path("./resultados"),
    pdfs_subdir="certificados_pdf",
    planilhas_subdir="planilhas_excel",
    dados_subdir="dados_csv",
    logo_path=Path("./assets/logo.png"),
    template_name="certificado.html",
    stylesheet_name="certificado.css",
    sobrescrever_existentes=True,
)

engine = CertificateEngine(config=config)

# Ou via dicionário (útil para JSON/YAML)
config = EngineConfig.from_dict({
    "output_dir": "./resultados",
    "logo_path": "./logo.png",
})
```

---

## 📁 Estrutura de Saída

```
results/
├── data/
│   ├── certificados.csv           # Dados principais dos certificados
│   ├── produtos_quimicos.csv      # Produtos por certificado
│   └── metodos_aplicacao.csv      # Métodos por certificado
├── pdfs/
│   └── nome-fantasia_12345678_001-2025_20251028-143022.pdf
├── spreadsheets/
│   └── planilha_consolidada.xlsx  # Única planilha com todos os dados
└── logs/
    └── processamento.log
```

### Nomeclatura de arquivos PDF

Os PDFs são salvos com nomes únicos para evitar sobrescrita:

**Formato**: `{nome_fantasia}_{cnpj_8dig}_{numero_cert}_{timestamp}.pdf`

**Exemplo**: `Empresa-Exemplo_11222333_001-2025_20251028-143022.pdf`

- Nome fantasia sanitizado (primeiros 30 caracteres)
- CNPJ (8 primeiros dígitos)
- Número do certificado (com `/` substituído por `-`)
- Timestamp no formato `YYYYMMDD-HHMMSS`

### Planilha consolidada

Uma **única planilha** `planilha_consolidada.xlsx` com dados de todos os certificados processados:

**Colunas principais:**
```
| id | numero_certificado | razao_social | cnpj | data_execucao | data_validade | 
| valor | bairro | cidade | nome_produto | classe_quimica | concentracao | 
| metodo | quantidade | ... |
```

---

## ⚙️ Configuração

### Via EngineConfig

```python
from pathlib import Path
from engine_excel_to_pdf import EngineConfig

config = EngineConfig(
    output_dir=Path("./results"),          # Diretório raiz de saída
    pdfs_subdir="pdfs",                    # results/pdfs/
    planilhas_subdir="spreadsheets",       # results/spreadsheets/
    dados_subdir="data",                   # results/data/
    logs_subdir="logs",                    # results/logs/
    assets_dir=Path("./assets"),           # Diretório de assets
    logo_path=Path("./assets/logo.png"),   # Logo para PDFs
    template_name="certificado.html",      # Template HTML
    stylesheet_name="certificado.css",     # Stylesheet CSS
    sobrescrever_existentes=False,         # Sobrescrever arquivos existentes
    validar_cnpj=True,                     # Validar CNPJ com checksum
    criar_backup=False,                    # Criar backup antes de sobrescrever
)

# Criar diretórios necessários
config.criar_diretorios()
```

### Via dicionário (JSON/YAML)

```python
from engine_excel_to_pdf import EngineConfig

config_dict = {
    "output_dir": "/app/resultados",
    "logo_path": "/app/assets/logo.png",
    "sobrescrever_existentes": True,
}

config = EngineConfig.from_dict(config_dict)
```

### Via variáveis de ambiente

```bash
export ENGINE_STORAGE_ROOT="/app/results"
export ENGINE_ASSETS_DIR="/app/assets"
```

```python
from engine_excel_to_pdf import CertificateEngine

# Usa automaticamente as variáveis de ambiente
engine = CertificateEngine()
```

### Campos opcionais do certificado

Os seguintes campos são **opcionais** e podem ser omitidos:

- `valor` - Valor monetário do serviço (ex: "R$ 1.500,00")
- `bairro` - Bairro do endereço (extraído automaticamente do endereço se não fornecido)
- `cidade` - Cidade do endereço (extraído automaticamente do endereço se não fornecido)

**Extração automática de bairro e cidade:**

Se o `endereco_completo` seguir o padrão `"Rua, Bairro, Cidade"` (separado por vírgulas), o sistema extrai automaticamente:

```python
payload = {
    "certificado": {
        "endereco_completo": "Rua das Flores, 123, Jardim Primavera, São Paulo/SP",
        # bairro será: "Jardim Primavera"
        # cidade será: "São Paulo/SP"
    }
}
```

---

## 💡 Exemplos de Uso

O projeto inclui vários arquivos de exemplo na raiz:

### `exemplos_uso.py`

Demonstra diferentes cenários de uso:
- Processamento básico de pasta
- Processamento paralelo
- Configuração customizada
- Configuração via dicionário
- Processamento de arquivo único
- Uso com variáveis de ambiente

```bash
python exemplos_uso.py
```

### `teste_valor.py`

Testa o campo opcional `valor`:
- Certificado COM campo valor
- Certificado SEM campo valor

```bash
python teste_valor.py
```

### `teste_campos_extras.py`

Testa os campos opcionais `bairro` e `cidade`:
- Fornecimento manual dos campos
- Extração automática do endereço completo

```bash
python teste_campos_extras.py
```

### `teste_skip_validation.py`

Demonstra o modo `skip_validation`:
- Validação habilitada (dados inválidos falham)
- Validação desabilitada (aceita qualquer dado)

```bash
python teste_skip_validation.py
```

---

## 🧪 Testes

```bash
# Rodar todos os testes com cobertura
pytest

# Ou com uv
uv run pytest

# Modo rápido (sem cobertura)
pytest --no-cov

# Testes em paralelo (mais rápido)
pytest -n auto

# Rodar testes específicos
pytest tests/test_validators.py
pytest tests/test_validators.py::test_validate_cnpj

# Ver relatório de cobertura HTML
pytest --cov-report=html
open htmlcov/index.html
```

### Estatísticas de Testes

- ✅ **71 testes** passando
- 📊 **84.7%** de cobertura geral
- 🎯 **96.6%** validators.py
- 🎯 **91.1%** config.py  
- 🎯 **90.0%** generators/

### Estrutura de Testes

```
tests/
├── conftest.py                 # Fixtures compartilhadas
├── test_batch_processor.py     # Testes de processamento em lote
├── test_config.py              # Testes de configuração
├── test_csv_manager.py         # Testes de persistência CSV
├── test_excel_extractor.py     # Testes de extração Excel
├── test_generators.py          # Testes de PDF e planilhas
├── test_interface.py           # Testes da interface principal
├── test_models.py              # Testes dos modelos de dados
├── test_utils.py               # Testes de utilidades
└── test_validators.py          # Testes de validação
```

---

## 📚 API Completa

### CertificateEngine (MotorCertificados)

```python
from engine_excel_to_pdf import CertificateEngine

# Inicialização
engine = CertificateEngine(
    config=None,              # EngineConfig opcional
    skip_validation=False,    # Pular validações
)

# Processar Excel
resultado = engine.processar_upload(arquivo: Path)
# Retorna: {"certificado": Certificado, "pdf": Path, "planilha": Path}

# Criar certificado manualmente
resultado = engine.criar_manual(payload: dict)
# Retorna: {"certificado": Certificado, "pdf": Path, "planilha": Path}

# Exportar certificado existente (regenera PDF)
resultado = engine.exportar_certificado(numero_certificado: str)
# Retorna: {"certificado": Certificado, "pdf": Path, "planilha": Path} ou None

# Listar todos os certificados
certificados: List[Certificado] = engine.listar_certificados()
```

### BatchProcessor

```python
from engine_excel_to_pdf import BatchProcessor

processor = BatchProcessor(
    motor=None,                      # CertificateEngine opcional
    extensoes=['.xlsx', '.xls'],     # Extensões aceitas
    max_workers=None,                # None=sequencial, int=paralelo
    skip_validation=False,           # Pular validações
)

resultados = processor.processar_pasta(
    pasta: Path,
    recursivo: bool = False,         # Processar subpastas
    continuar_erro: bool = True,     # Continuar mesmo com erros
)
# Retorna: {"sucessos": List[ProcessingResult], 
#           "erros": List[ProcessingResult], 
#           "total": int}
```

### Modelos de Dados

```python
from engine_excel_to_pdf import Certificado, ProdutoQuimico, MetodoAplicacao

# Certificado
certificado = Certificado(
    numero_certificado: str,
    numero_licenca: str,
    razao_social: str,
    nome_fantasia: str,
    cnpj: str,
    endereco_completo: str,
    data_execucao: date,
    data_validade: date,
    pragas_tratadas: str,
    arquivo_origem: str,
    data_cadastro: datetime,
    id: Optional[str] = None,        # Gerado automaticamente (hash)
    valor: Optional[str] = None,     # Opcional
    bairro: Optional[str] = None,    # Opcional
    cidade: Optional[str] = None,    # Opcional
)

# Produto Químico
produto = ProdutoQuimico(
    nome_produto: str,
    classe_quimica: str,
    concentracao: Optional[float],   # Decimal (0.025 = 2.5%)
)

# Método de Aplicação
metodo = MetodoAplicacao(
    metodo: str,
    quantidade: str,
)
```

### Validação

```python
from engine_excel_to_pdf import CertificadoValidator, ValidationError

try:
    # Validar estrutura do payload
    CertificadoValidator.validate_payload_structure(payload)
    
    # Validar certificado
    CertificadoValidator.validate_certificado(certificado)
    
    # Validar produtos
    CertificadoValidator.validate_produtos(produtos)
    
    # Validar métodos
    CertificadoValidator.validate_metodos(metodos)
    
    # Validar tudo junto
    CertificadoValidator.validate_bundle(bundle)
    
except ValidationError as e:
    print(f"Erros de validação:")
    for erro in e.errors:
        print(f"  - {erro}")
```

---

## 🎨 Customização de Templates

Os templates HTML/CSS ficam em `engine_excel_to_pdf/assets/templates/`:

### certificado.html - Estrutura do PDF

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Certificado {{ certificate.numero_certificado }}</title>
</head>
<body>
    <header>
        {% if logo_url %}
        <img src="{{ logo_url }}" alt="Logo" class="logo">
        {% endif %}
        <h1>{{ certificate.razao_social }}</h1>
        <p>{{ certificate.bairro }} - {{ certificate.cidade }}</p>
    </header>
    
    <section class="info">
        <p><strong>CNPJ:</strong> {{ certificate.cnpj }}</p>
        <p><strong>Endereço:</strong> {{ certificate.endereco }}</p>
    </section>
    
    <section class="produtos">
        <h2>Produtos Químicos</h2>
        {% for produto in produtos %}
        <div class="produto">
            <span>{{ produto.nome }}</span>
            <span>{{ produto.classe }}</span>
            <span>{{ produto.concentracao }}</span>
        </div>
        {% endfor %}
    </section>
    
    <section class="metodos">
        <h2>Métodos de Aplicação</h2>
        {% for metodo in metodos %}
        <div class="metodo">
            <span>{{ metodo.nome }}</span>
            <span>{{ metodo.quantidade }}</span>
        </div>
        {% endfor %}
    </section>
</body>
</html>
```

### certificado.css - Estilos

```css
@page {
    size: A4;
    margin: 2cm;
}

body {
    font-family: 'Arial', sans-serif;
    font-size: 10pt;
    color: #333;
}

header {
    text-align: center;
    margin-bottom: 2cm;
    border-bottom: 2px solid #0066cc;
}

.logo {
    max-width: 200px;
    height: auto;
}

h1 {
    color: #0066cc;
    font-size: 18pt;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 8px;
    text-align: left;
    border: 1px solid #ddd;
}
```

### Variáveis disponíveis no template

```python
{
    "certificate": {
        "numero_certificado": str,
        "razao_social": str,
        "nome_fantasia": str,
        "cnpj": str,
        "endereco": str,
        "pragas": str,
        "bairro": str,          # Pode ser placeholder se não fornecido
        "cidade": str,          # Pode ser placeholder se não fornecido
    },
    "certificate_meta": [       # Metadados do certificado
        {"label": "Nº Certificado", "value": "..."},
        {"label": "Nº Licença", "value": "..."},
        # ...
    ],
    "produtos": [
        {
            "nome": str,
            "classe": str,
            "concentracao": str,  # Ex: "2.5%" ou placeholder
        }
    ],
    "metodos": [
        {
            "nome": str,
            "quantidade": str,
        }
    ],
    "logo_url": str,            # URI do logo (file://...)
    "placeholder": str,         # Valor padrão para campos vazios
}
```

---

## 📦 Estrutura do Projeto

```
engine_excel_to_pdf/
├── __init__.py                    # API pública e exports
├── interface.py                   # MotorCertificados (facade principal)
├── batch_processor.py             # Processamento em lote sequencial/paralelo
├── config.py                      # EngineConfig (configuração customizável)
├── config_defaults.py             # Configurações e paths padrão
├── constants.py                   # Constantes do projeto
├── models.py                      # Dataclasses (Certificado, Produto, Método)
├── validators.py                  # Validação de dados e regras de negócio
├── utils.py                       # Utilidades (CNPJ, datas, normalização)
├── settings.py                    # Configurações globais e variáveis de ambiente
├── extractor/
│   ├── __init__.py
│   └── excel_extractor.py         # Extração de dados de Excel
├── generators/
│   ├── __init__.py
│   ├── pdf_generator.py           # Geração de PDF com WeasyPrint
│   └── spreadsheet_generator.py   # Geração de planilha consolidada
├── storage/
│   ├── __init__.py
│   └── csv_manager.py             # Persistência em CSV
└── assets/
    └── templates/
        ├── certificado.html       # Template HTML do PDF
        └── certificado.css        # Estilos CSS do PDF
```

### Componentes principais

- **`CertificateEngine`**: Interface principal (facade)
- **`BatchProcessor`**: Processamento em lote com threading
- **`ExcelExtractor`**: Extração de dados de planilhas Excel
- **`PDFGenerator`**: Geração de PDFs usando Jinja2 + WeasyPrint
- **`SpreadsheetGenerator`**: Geração de planilha consolidada
- **`CsvManager`**: Persistência em arquivos CSV
- **`CertificadoValidator`**: Validações de negócio

---

## 🔧 CLI (Command Line Interface)

```bash
# Processar arquivo único
python main.py certificado.xlsx

# Processar pasta inteira (sequencial)
python main.py --pasta ./certificados

# Processar recursivamente com paralelização (4 workers)
python main.py --pasta ./certificados --recursivo --paralelo 4

# Customizar diretório de saída
python main.py --pasta ./certificados --output ./resultados

# Pular validações (aceitar qualquer dado)
python main.py arquivo.xlsx --skip-validation

# Ver ajuda completa
python main.py --help
```

### Opções disponíveis

```
positional arguments:
  arquivo                   Arquivo Excel único para processar

options:
  -h, --help               Mostrar ajuda
  --pasta PASTA            Pasta com múltiplos arquivos Excel
  --recursivo, -r          Processar subpastas recursivamente
  --paralelo N, -p N       Número de workers paralelos (ex: 4)
  --output DIR, -o DIR     Diretório de saída customizado
  --skip-validation        Pular validações (aceitar qualquer dado)
```

---

## 🔐 Validação de CNPJ

O sistema inclui **validação completa de CNPJ** com verificação de dígitos verificadores:

```python
from engine_excel_to_pdf.utils import validate_cnpj, extract_cnpj, format_cnpj

# Validar CNPJ (apenas dígitos)
is_valid = validate_cnpj("11222333000181")  # True ou False

# Extrair e formatar CNPJ de texto
cnpj = extract_cnpj("CNPJ: 11.222.333/0001-81")  # "11.222.333/0001-81"

# Formatar CNPJ
formatted = format_cnpj("11222333000181")  # "11.222.333/0001-81"
```

### Algoritmo de Validação

- Verifica se possui 14 dígitos
- Rejeita CNPJs com todos os dígitos iguais (ex: "11111111111111")
- Calcula e valida os dois dígitos verificadores usando os pesos oficiais
- Segue exatamente o algoritmo da Receita Federal

### Desabilitar Validação

```python
# Para testes ou quando os dados vêm de fonte confiável
engine = CertificateEngine(skip_validation=True)
```

---

## 🤝 Compatibilidade de API

### API Moderna (recomendada)

```python
from engine_excel_to_pdf import CertificateEngine

engine = CertificateEngine()
resultado = engine.processar_upload(arquivo)
```

### API Legada (backward compatible)

```python
from engine_excel_to_pdf import MotorCertificados

motor = MotorCertificados()
resultado = motor.processar_upload(arquivo)
```

**Nota**: Ambas as APIs são idênticas. `CertificateEngine` é apenas um alias para `MotorCertificados`.

### Aliases de Campos no Payload

O sistema aceita **nomes alternativos** para os campos:

```python
payload = {
    "certificado": {
        # Aceita "numero" OU "numero_certificado"
        "numero": "001/2025",
        
        # Aceita "licenca" OU "numero_licenca"  
        "licenca": "LIC-123",
        
        # Aceita "endereco" OU "endereco_completo"
        "endereco": "Rua X, 123",
    },
    "produtos": [
        {
            # Aceita "nome" OU "nome_produto"
            "nome": "Produto A",
            
            # Aceita "classe" OU "classe_quimica"
            "classe": "Piretroide",
        }
    ],
    "metodos": [
        {
            # Aceita "descricao" OU "metodo"
            "descricao": "Pulverização",
        }
    ],
}
```

---

## 🤝 Compatibilidade

### API Moderna (recomendada)

```python
from engine_excel_to_pdf import CertificateEngine

engine = CertificateEngine()
```

### API Legada (backward compatible)

```python
from engine_excel_to_pdf import MotorCertificados

motor = MotorCertificados()
```

Ambas funcionam exatamente da mesma forma!

---

## � Tratamento de Erros

### ValidationError

Lançado quando os dados não passam nas validações:

```python
from engine_excel_to_pdf import CertificateEngine, ValidationError

engine = CertificateEngine()

try:
    resultado = engine.criar_manual(payload)
except ValidationError as e:
    print("Erros encontrados:")
    for erro in e.errors:
        print(f"  - {erro}")
    # Exemplo de erros:
    # - Required field missing: razao_social
    # - Invalid or missing CNPJ
    # - Expiration date is before execution date
```

### FileNotFoundError

Lançado quando arquivo ou pasta não existe:

```python
try:
    resultado = engine.processar_upload(Path("arquivo_inexistente.xlsx"))
except FileNotFoundError as e:
    print(f"Arquivo não encontrado: {e}")
```

### Outros Erros

```python
from pathlib import Path

try:
    resultado = processor.processar_pasta(Path("pasta"))
except FileNotFoundError:
    print("Pasta não encontrada")
except ValueError:
    print("Caminho não é um diretório")
except Exception as e:
    print(f"Erro inesperado: {e}")
```

---

##  Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 👥 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. **Fork** o repositório
2. **Clone** seu fork: `git clone https://github.com/JulianoL13/engine-excel-to-pdf.git`
3. **Crie um branch**: `git checkout -b feature/minha-feature`
4. **Faça suas alterações** e adicione testes
5. **Execute os testes**: `pytest`
6. **Commit**: `git commit -m "Adiciona minha feature"`
7. **Push**: `git push origin feature/minha-feature`
8. **Abra um Pull Request**

### Guidelines

- Mantenha a cobertura de testes acima de 80%
- Use type hints em todo o código
- Siga PEP 8 (formatação de código Python)
- Documente novas funcionalidades no README
- Adicione testes para novas funcionalidades

---

## �️ Roadmap

### Futuras Melhorias

- [ ] Suporte a templates personalizados por cliente
- [ ] Exportação para outros formatos (JSON, XML)
- [ ] API REST com FastAPI
- [ ] Interface web para upload e processamento
- [ ] Geração de relatórios estatísticos
- [ ] Suporte a múltiplos idiomas
- [ ] Cache de PDFs gerados
- [ ] Assinatura digital de PDFs
- [ ] Integração com armazenamento em nuvem (S3, Google Drive)

---

## 📞 Suporte

- 🐛 **Bugs**: [Reportar issues](https://github.com/JulianoL13/engine-excel-to-pdf/issues)
- 💡 **Features**: [Solicitar funcionalidades](https://github.com/JulianoL13/engine-excel-to-pdf/issues)
- 📖 **Documentação**: [Wiki do projeto](https://github.com/JulianoL13/engine-excel-to-pdf/wiki)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/JulianoL13/engine-excel-to-pdf/discussions)

---

## ✨ Agradecimentos

Desenvolvido com ❤️ usando:
- [OpenPyXL](https://openpyxl.readthedocs.io/) - Manipulação de Excel
- [WeasyPrint](https://weasyprint.org/) - Geração de PDFs
- [Jinja2](https://jinja.palletsprojects.com/) - Templates
- [pytest](https://pytest.org/) - Testes

---

**Engine Excel to PDF** - Transformando planilhas em certificados profissionais desde 2025 🚀


