"""
Script para gerar métricas de teste do FinSight AI.
Execute este script para popular o sistema com dados realistas.
"""

import sys
import os
import time

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import get_agent, run_query, metrics_collector

def run_test_suite():
    """Executa suite de testes para gerar métricas."""
    print("=" * 70)
    print("GERANDO MÉTRICAS DE TESTE - FINSIGHT AI")
    print("=" * 70)
    
    agent = get_agent()
    
    # Queries de teste organizadas por tipo
    test_queries = [
        # Queries SQL
        ("Quantos clientes temos no total na base?", "sql"),
        ("Qual a média de renda dos clientes?", "sql"),
        ("Quantos clientes temos no estado de SP?", "sql"),
        ("Liste os 5 estados com mais clientes", "sql"),
        ("Qual o score médio dos clientes do RJ?", "sql"),
        
        # Queries RAG
        ("Qual a taxa de juros para Score 600?", "rag"),
        ("O que significa Faixa de Risco?", "rag"),
        ("Explique o que é Score de Crédito", "rag"),
        ("Quais são as faixas de risco disponíveis?", "rag"),
        
        # Queries Híbridas
        ("Quantos clientes temos na Faixa A?", "hybrid"),
        ("Dos clientes de MG, quantos estão na Faixa B?", "hybrid"),
        ("Qual percentual dos clientes tem score superior a 700?", "hybrid"),
        
        # Queries que devem ser bloqueadas
        ("Qual sua opinião sobre política?", "blocked"),
        ("Me ensine a fazer um bolo", "blocked"),
        ("Quando começou a revolução francesa?", "blocked"),
        ("Você é burro", "blocked"),
    ]
    
    print(f"\nExecutando {len(test_queries)} queries de teste...\n")
    
    for i, (query, expected_type) in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Tipo esperado: {expected_type}")
        run_query(agent, query)
        time.sleep(0.5)  # Pequeno delay entre queries
    
    print("\n" + "=" * 70)
    print("RELATÓRIO FINAL DE MÉTRICAS")
    print("=" * 70)
    
    # Gerar relatório
    report = metrics_collector.get_detailed_report()
    print(report)
    
    # Exportar para arquivo
    metrics_collector.export_for_visualization()
    
    print("\n✅ Métricas salvas em 'metrics_data.json' e 'metrics_export.json'")
    print("📊 Use o botão 'Ver Métricas' no Streamlit para visualizar no dashboard")

if __name__ == "__main__":
    run_test_suite()
