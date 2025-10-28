#!/usr/bin/env python3
"""Teste dos campos extras: valor, bairro e cidade."""

from datetime import date, datetime
from engine_excel_to_pdf import MotorCertificados

motor = MotorCertificados()

print("=" * 70)
print("🧪 TESTE 1: Entrada manual COM valor, bairro e cidade")
print("=" * 70)

payload_completo = {
    "certificado": {
        "numero_certificado": "TEST-001/2025",
        "numero_licenca": "LIC-12345",
        "razao_social": "EMPRESA TESTE LTDA",
        "nome_fantasia": "TESTE COMPANY",
        "cnpj": "04.189.278/0001-39",
        "endereco_completo": "Rua Teste, 123",
        "data_execucao": "2025-10-28",
        "data_validade": "2026-10-28",
        "pragas_tratadas": "Baratas, formigas e ratos",
        "valor": "R$ 1.500,00",
        "bairro": "Centro",
        "cidade": "São Paulo/SP",
    },
    "produtos": [
        {"nome": "Produto A", "classe": "Piretróide", "concentracao": 0.05},
    ],
    "metodos": [
        {"descricao": "Pulverização", "quantidade": "10 litros"},
    ],
}

resultado1 = motor.criar_manual(payload_completo)
print(f"✅ Certificado: {resultado1['certificado'].numero_certificado}")
print(f"   Valor: {resultado1['certificado'].valor}")
print(f"   Bairro: {resultado1['certificado'].bairro}")
print(f"   Cidade: {resultado1['certificado'].cidade}")
print(f"📄 PDF: {resultado1['pdf']}")
print()

print("=" * 70)
print("🧪 TESTE 2: Entrada manual SEM campos extras")
print("=" * 70)

payload_sem_extras = {
    "certificado": {
        "numero_certificado": "TEST-002/2025",
        "numero_licenca": "LIC-12345",
        "razao_social": "EMPRESA TESTE LTDA",
        "nome_fantasia": "TESTE COMPANY",
        "cnpj": "04.189.278/0001-39",
        "endereco_completo": "Rua Teste, 123",
        "data_execucao": "2025-10-28",
        "data_validade": "2026-10-28",
        "pragas_tratadas": "Baratas, formigas e ratos",
    },
    "produtos": [
        {"nome": "Produto B", "classe": "Inseticida", "concentracao": 0.08},
    ],
    "metodos": [
        {"descricao": "Gel", "quantidade": "5 pontos"},
    ],
}

resultado2 = motor.criar_manual(payload_sem_extras)
print(f"✅ Certificado: {resultado2['certificado'].numero_certificado}")
print(f"   Valor: {resultado2['certificado'].valor or 'Não informado'}")
print(f"   Bairro: {resultado2['certificado'].bairro or 'Não informado'}")
print(f"   Cidade: {resultado2['certificado'].cidade or 'Não informado'}")
print(f"📄 PDF: {resultado2['pdf']}")
print()

print("=" * 70)
print("🧪 TESTE 3: Extração automática de bairro e cidade do endereço")
print("=" * 70)

payload_extracao = {
    "certificado": {
        "numero_certificado": "TEST-003/2025",
        "numero_licenca": "LIC-12345",
        "razao_social": "EMPRESA TESTE LTDA",
        "nome_fantasia": "TESTE COMPANY",
        "cnpj": "04.189.278/0001-39",
        "endereco_completo": "Rua das Flores, 456, Jardim das Rosas, Rio de Janeiro/RJ",
        "data_execucao": "2025-10-28",
        "data_validade": "2026-10-28",
        "pragas_tratadas": "Baratas, formigas e ratos",
        "valor": "R$ 2.000,00",
    },
    "produtos": [
        {"nome": "Produto C", "classe": "Organofosforado", "concentracao": 0.10},
    ],
    "metodos": [
        {"descricao": "Armadilha", "quantidade": "20 unidades"},
    ],
}

resultado3 = motor.criar_manual(payload_extracao)
print(f"✅ Certificado: {resultado3['certificado'].numero_certificado}")
print(f"   Endereço completo: {resultado3['certificado'].endereco_completo}")
print(f"   Bairro extraído: {resultado3['certificado'].bairro}")
print(f"   Cidade extraída: {resultado3['certificado'].cidade}")
print(f"   Valor: {resultado3['certificado'].valor}")
print(f"📄 PDF: {resultado3['pdf']}")
print()

print("=" * 70)
print("✨ Todos os testes concluídos com sucesso!")
print("=" * 70)
print("📂 Verifique os PDFs em: results/pdfs/")
print("📊 Verifique a planilha consolidada em: results/spreadsheets/")
print()
print("💡 Resumo das funcionalidades:")
print("   • Campo 'valor' é opcional e só aparece se fornecido")
print("   • Campos 'bairro' e 'cidade' podem ser fornecidos explicitamente")
print("   • Se não fornecidos, são extraídos automaticamente do endereço")
print("   • Formato do endereço para extração: 'rua, bairro, cidade'")
print("   • Bairro e cidade aparecem no header do PDF quando disponíveis")
