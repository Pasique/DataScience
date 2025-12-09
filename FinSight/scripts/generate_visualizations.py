"""
Gera visualizações das métricas coletadas para apresentação.
Requer: matplotlib, seaborn
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# Configuração de estilo
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def load_metrics(file_path="../outputs/metrics_export.json"):
    """Carrega métricas do arquivo JSON."""
    if not Path(file_path).exists():
        print(f"❌ Arquivo {file_path} não encontrado.")
        print("Execute primeiro: python scripts/test_metrics.py")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_visualizations(data):
    """Cria todas as visualizações."""
    summary = data['summary']
    raw_metrics = data['raw_metrics']
    
    # Criar figura com subplots
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('FinSight AI - Dashboard de Métricas', fontsize=20, fontweight='bold')
    
    # 1. Distribuição de Tipos de Query
    ax1 = plt.subplot(2, 3, 1)
    types = summary['distribuicao_queries']
    colors = {'sql': '#3498db', 'rag': '#2ecc71', 'hybrid': '#f39c12', 'blocked': '#e74c3c', 'error': '#95a5a6'}
    ax1.pie(types.values(), labels=types.keys(), autopct='%1.1f%%', 
            colors=[colors.get(k, '#95a5a6') for k in types.keys()],
            startangle=90)
    ax1.set_title('Distribuição de Tipos de Query', fontweight='bold')
    
    # 2. Tempo de Resposta
    ax2 = plt.subplot(2, 3, 2)
    response_times = [m['response_time'] for m in raw_metrics if m['query_type'] != 'blocked']
    if response_times:
        ax2.hist(response_times, bins=15, color='#3498db', alpha=0.7, edgecolor='black')
        ax2.axvline(summary['tempo_resposta']['media_segundos'], 
                   color='red', linestyle='--', linewidth=2, label='Média')
        ax2.axvline(summary['tempo_resposta']['mediana_segundos'], 
                   color='green', linestyle='--', linewidth=2, label='Mediana')
        ax2.set_xlabel('Tempo (segundos)')
        ax2.set_ylabel('Frequência')
        ax2.set_title('Distribuição de Tempo de Resposta', fontweight='bold')
        ax2.legend()
    
    # 3. Taxa de Sucesso
    ax3 = plt.subplot(2, 3, 3)
    success_data = [
        summary['performance']['queries_bem_sucedidas'],
        summary['performance']['queries_com_erro'],
        summary['guardrails']['total_bloqueadas']
    ]
    labels = ['Sucesso', 'Erro', 'Bloqueadas']
    colors_bar = ['#2ecc71', '#e74c3c', '#f39c12']
    ax3.bar(labels, success_data, color=colors_bar, alpha=0.7, edgecolor='black')
    ax3.set_ylabel('Quantidade')
    ax3.set_title('Performance Geral do Sistema', fontweight='bold')
    for i, v in enumerate(success_data):
        ax3.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
    
    # 4. Timeline de Queries
    ax4 = plt.subplot(2, 3, 4)
    timestamps = [datetime.fromisoformat(m['timestamp']) for m in raw_metrics]
    response_times_all = [m['response_time'] for m in raw_metrics]
    colors_timeline = [colors.get(m['query_type'], '#95a5a6') for m in raw_metrics]
    ax4.scatter(timestamps, response_times_all, c=colors_timeline, alpha=0.6, s=100, edgecolors='black')
    ax4.set_xlabel('Timestamp')
    ax4.set_ylabel('Tempo de Resposta (s)')
    ax4.set_title('Timeline de Queries', fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    
    # 5. Impacto dos Guardrails
    ax5 = plt.subplot(2, 3, 5)
    total = summary['periodo']['total_queries']
    blocked = summary['guardrails']['total_bloqueadas']
    executed = total - blocked
    
    categories = ['Queries\nExecutadas', 'Queries\nBloqueadas']
    values = [executed, blocked]
    colors_guard = ['#3498db', '#e74c3c']
    bars = ax5.bar(categories, values, color=colors_guard, alpha=0.7, edgecolor='black')
    ax5.set_ylabel('Quantidade')
    ax5.set_title('Impacto dos Guardrails', fontweight='bold')
    
    # Adicionar valores e economia
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(val)}', ha='center', fontweight='bold')
    
    # Texto de economia
    economy_text = f"Economia:\n~{summary['guardrails']['economia_estimada_tokens']:,} tokens\n{summary['guardrails']['economia_estimada_usd']}"
    ax5.text(0.5, 0.95, economy_text, transform=ax5.transAxes,
            fontsize=9, verticalalignment='top', bbox=dict(boxstyle='round', 
            facecolor='wheat', alpha=0.5))
    
    # 6. Métricas Principais (KPIs)
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    kpi_text = f"""
    MÉTRICAS PRINCIPAIS (KPIs)
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    📊 Total de Queries: {total}
    
    ✅ Taxa de Sucesso: {summary['performance']['taxa_sucesso']}
    
    ⚡ Tempo Médio: {summary['tempo_resposta']['media_segundos']}s
    
    🛡️ Taxa de Bloqueio: {summary['guardrails']['taxa_bloqueio']}
    
    💰 Custo Total: {summary['custos']['custo_total_usd']}
    
    💾 Total de Tokens: {summary['custos']['total_tokens']:,}
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    ax6.text(0.1, 0.9, kpi_text, transform=ax6.transAxes,
            fontsize=11, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    plt.tight_layout()
    
    # Salvar figura
    output_file = '../outputs/metrics_dashboard.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Dashboard salvo em: {output_file}")
    
    # Mostrar
    plt.show()

def create_summary_image(data):
    """Cria imagem resumida para LinkedIn."""
    summary = data['summary']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    title_text = "🔐 FinSight AI - Resultados do Projeto"
    
    results_text = f"""
    
    {title_text}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    📊 PERFORMANCE
       • {summary['periodo']['total_queries']} queries processadas
       • {summary['performance']['taxa_sucesso']} taxa de sucesso
       • {summary['tempo_resposta']['media_segundos']}s tempo médio de resposta
    
    🛡️ SEGURANÇA (Guardrails)
       • {summary['guardrails']['total_bloqueadas']} queries bloqueadas ({summary['guardrails']['taxa_bloqueio']})
       • ~{summary['guardrails']['economia_estimada_tokens']:,} tokens economizados
       • {summary['guardrails']['economia_estimada_usd']} em custos evitados
    
    🎯 CAPACIDADES
       • SQL: Consultas complexas em base de dados
       • RAG: Políticas e glossário financeiro
       • Híbrido: Análises combinadas multi-fonte
    
    💰 EFICIÊNCIA
       • Custo total: {summary['custos']['custo_total_usd']}
       • {summary['custos']['total_tokens']:,} tokens processados
       • Custo médio: {summary['custos']['custo_medio_por_query']} por query
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Stack: Python | LangChain | LangGraph | OpenAI | ChromaDB
    """
    
    ax.text(0.1, 0.95, results_text, transform=ax.transAxes,
           fontsize=12, verticalalignment='top', fontfamily='monospace',
           bbox=dict(boxstyle='round', facecolor='#ecf0f1', alpha=0.9, pad=1))
    
    output_file = '../outputs/project_results_linkedin.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Imagem para LinkedIn salva em: {output_file}")
    plt.show()

if __name__ == "__main__":
    print("Gerando visualizações das métricas...\n")
    
    data = load_metrics()
    if data:
        print("📊 Criando dashboard completo...")
        create_visualizations(data)
        
        print("\n📱 Criando imagem para LinkedIn...")
        create_summary_image(data)
        
        print("\n✅ Todas as visualizações foram geradas!")
        print("📁 Arquivos criados em outputs/:")
        print("   - metrics_dashboard.png (dashboard completo)")
        print("   - project_results_linkedin.png (resumo para LinkedIn)")
    else:
        print("\n⚠️ Execute primeiro: python scripts/test_metrics.py")
