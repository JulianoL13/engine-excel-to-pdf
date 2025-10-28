#!/usr/bin/env python3
"""Teste do campo valor opcional."""

from datetime import date, datetime
from engine_excel_to_pdf import MotorCertificados

motor = MotorCertificados()

payload_com_valor = {
    "certificado": {
        "numero_certificado": "TEST-001/2025",
        "numero_licenca": "LIC-12345",
        "razao_social": "EMPRESA TESTE LTDA",
        "nome_fantasia": "TESTE COMPANY",
        "cnpj": "12.345.678/0001-90",
        "endereco_completo": "Rua Teste, 123 - Centro - São Paulo/SP",
        "data_execucao": "2025-10-28",
        "data_validade": "2026-10-28",
        "pragas_tratadas": "Baratas, formigas e ratos",
        "valor": "R$ 1.500,00",
    },
    "produtos": [
        {
            "nome": "Produto A",
            "classe": "Piretróide",
            "concentracao": 0.05,
        },
        {
            "nome": "Produto B",
            "classe": "Organofosforado",
            "concentracao": 0.10,
        },
    ],
    "metodos": [
        {
            "descricao": "Pulverização",
            "quantidade": "10 litros",
        },
    ],
}

payload_sem_valor = {
    "certificado": {
        "numero_certificado": "TEST-002/2025",
        "numero_licenca": "LIC-12345",
        "razao_social": "EMPRESA TESTE LTDA",
        "nome_fantasia": "TESTE COMPANY",
        "cnpj": "12.345.678/0001-90",
        "endereco_completo": "Rua Teste, 123 - Centro - São Paulo/SP",
        "data_execucao": "2025-10-28",
        "data_validade": "2026-10-28",
        "pragas_tratadas": "Baratas, formigas e ratos",
    },
    "produtos": [
        {
            "nome": "Produto C",
            "classe": "Inseticida",
            "concentracao": 0.08,
        },
    ],
    "metodos": [
        {
            "descricao": "Gel",
            "quantidade": "5 pontos",
        },
    ],
}

print("🧪 Teste 1: Certificado COM campo valor")
resultado1 = motor.criar_manual(payload_com_valor)
print(f"✅ Certificado: {resultado1['certificado'].numero_certificado}")
print(f"✅ Valor: {resultado1['certificado'].valor}")
print(f"📄 PDF: {resultado1['pdf']}")
print(f"📊 Planilha: {resultado1['planilha']}")
print()

print("🧪 Teste 2: Certificado SEM campo valor")
resultado2 = motor.criar_manual(payload_sem_valor)
print(f"✅ Certificado: {resultado2['certificado'].numero_certificado}")
print(f"✅ Valor: {resultado2['certificado'].valor}")
print(f"📄 PDF: {resultado2['pdf']}")
print(f"📊 Planilha: {resultado2['planilha']}")
print()

print("✨ Testes concluídos!")
print("📂 Verifique os arquivos em results/pdfs/ e results/spreadsheets/")
