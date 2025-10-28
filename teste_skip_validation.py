#!/usr/bin/env python3
"""Teste da flag skip_validation."""

from datetime import date, datetime
from engine_excel_to_pdf import MotorCertificados

print("=" * 70)
print("🧪 TESTE: Flag skip_validation")
print("=" * 70)
print()

print("📋 Teste 1: COM validação (CNPJ inválido)")
print("-" * 70)

motor_com_validacao = MotorCertificados(skip_validation=False)

payload_invalido = {
    "certificado": {
        "numero_certificado": "TEST-INVALID/2025",
        "numero_licenca": "LIC-99999",
        "razao_social": "EMPRESA TESTE LTDA",
        "nome_fantasia": "TESTE COMPANY",
        "cnpj": "12.345.678/0001-99",
        "endereco_completo": "Rua Teste, 123, Centro, São Paulo/SP",
        "data_execucao": "2025-10-28",
        "data_validade": "2026-10-28",
        "pragas_tratadas": "Baratas e formigas",
    },
    "produtos": [
        {"nome": "Produto A", "classe": "Piretróide", "concentracao": 0.05},
    ],
    "metodos": [
        {"descricao": "Pulverização", "quantidade": "10 litros"},
    ],
}

try:
    resultado1 = motor_com_validacao.criar_manual(payload_invalido)
    print("❌ ERRO: Deveria ter falhado na validação!")
except Exception as e:
    print(f"✅ Validação funcionou: {e}")
    print()

print("📋 Teste 2: SEM validação (aceita qualquer dado)")
print("-" * 70)

motor_sem_validacao = MotorCertificados(skip_validation=True)

try:
    resultado2 = motor_sem_validacao.criar_manual(payload_invalido)
    print(f"✅ Certificado criado SEM validação:")
    print(f"   Número: {resultado2['certificado'].numero_certificado}")
    print(f"   CNPJ: {resultado2['certificado'].cnpj}")
    print(f"   PDF: {resultado2['pdf']}")
    print()
except Exception as e:
    print(f"❌ ERRO inesperado: {e}")
    print()

print("📋 Teste 3: Dados completamente malformados")
print("-" * 70)

payload_maluco = {
    "certificado": {
        "numero_certificado": "QUALQUER-COISA",
        "numero_licenca": "123",
        "razao_social": "X",
        "nome_fantasia": "Y",
        "cnpj": "invalido",
        "endereco_completo": "abc",
        "data_execucao": "2025-10-28",
        "data_validade": "2026-10-28",
        "pragas_tratadas": "z",
        "valor": "R$ 999.999,99",
        "bairro": "Bairro Qualquer",
        "cidade": "Cidade Qualquer",
    },
    "produtos": [
        {"nome": "X", "classe": "Y", "concentracao": 0.99},
    ],
    "metodos": [
        {"descricao": "Método X", "quantidade": "999"},
    ],
}

try:
    resultado3 = motor_sem_validacao.criar_manual(payload_maluco)
    print(f"✅ Certificado criado com dados malucos:")
    print(f"   Número: {resultado3['certificado'].numero_certificado}")
    print(f"   CNPJ: {resultado3['certificado'].cnpj}")
    print(f"   Bairro: {resultado3['certificado'].bairro}")
    print(f"   Cidade: {resultado3['certificado'].cidade}")
    print(f"   Valor: {resultado3['certificado'].valor}")
    print(f"   PDF: {resultado3['pdf']}")
    print()
except Exception as e:
    print(f"❌ ERRO: {e}")
    print()

print("=" * 70)
print("✨ Testes concluídos!")
print("=" * 70)
print()
print("💡 Resumo:")
print("   • skip_validation=False: Aplica todas as validações (padrão)")
print("   • skip_validation=True: Aceita qualquer dado sem validar")
print("   • Útil para testes ou quando os dados vêm de fonte confiável")
print()
