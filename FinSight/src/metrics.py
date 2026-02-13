"""Sistema de métricas para rastrear performance e custos do FinSight."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import statistics


@dataclass
class QueryMetric:
    """Dados de uma query individual."""
    timestamp: str
    query: str
    query_type: str  # 'sql', 'rag', 'hybrid', 'blocked'
    response_time: float
    tokens_used: int
    cost_usd: float
    success: bool
    error: str = None
    blocked_reason: str = None
    sql_query: str = None


class MetricsCollector:
    """Coleta e analisa métricas do sistema."""
    
    def __init__(self, metrics_file: str = "outputs/metrics_data.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics: List[Dict] = self._load_metrics()
        
    def _load_metrics(self) -> List[Dict]:
        """Carrega métricas do disco."""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_metrics(self):
        """Persiste métricas em disco."""
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
    
    def log_query(self, 
                  query: str,
                  query_type: str,
                  response_time: float,
                  tokens_used: int = 0,
                  success: bool = True,
                  error: str = None,
                  blocked_reason: str = None,
                  sql_query: str = None):
        """Registra uma query executada."""
        # Custo aproximado GPT-4o-mini: $0.15/1M input + $0.60/1M output
        # Assumindo split 50/50
        cost_usd = (tokens_used / 1_000_000) * 0.375
        
        metric = QueryMetric(
            timestamp=datetime.now().isoformat(),
            query=query[:100],  # Trunca para privacidade
            query_type=query_type,
            response_time=response_time,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            success=success,
            error=error,
            blocked_reason=blocked_reason,
            sql_query=sql_query
        )
        
        self.metrics.append(asdict(metric))
        self._save_metrics()
    
    def get_summary(self) -> Dict[str, Any]:
        """Gera resumo estatístico das métricas coletadas."""
        if not self.metrics:
            return {"error": "Nenhuma métrica coletada ainda"}
        
        total_queries = len(self.metrics)
        successful = sum(1 for m in self.metrics if m['success'])
        blocked = sum(1 for m in self.metrics if m['query_type'] == 'blocked')
        
        executed_queries = [m for m in self.metrics if m['query_type'] != 'blocked']
        
        response_times = [m['response_time'] for m in executed_queries]
        total_tokens = sum(m['tokens_used'] for m in self.metrics)
        total_cost = sum(m['cost_usd'] for m in self.metrics)
        
        type_distribution = {}
        for m in self.metrics:
            qtype = m['query_type']
            type_distribution[qtype] = type_distribution.get(qtype, 0) + 1
        
        # Análise detalhada por tipo
        analysis_by_type = {}
        for qtype in ['sql', 'rag', 'hybrid']:
            type_metrics = [m for m in self.metrics if m['query_type'] == qtype]
            if type_metrics:
                type_times = [m['response_time'] for m in type_metrics]
                type_tokens = sum(m['tokens_used'] for m in type_metrics)
                type_cost = sum(m['cost_usd'] for m in type_metrics)
                
                analysis_by_type[qtype] = {
                    "count": len(type_metrics),
                    "avg_time": round(statistics.mean(type_times), 2) if type_times else 0,
                    "total_tokens": type_tokens,
                    "total_cost": f"${type_cost:.4f}",
                    "avg_cost": f"${(type_cost/len(type_metrics)):.4f}" if type_metrics else "$0"
                }
        
        summary = {
            "periodo": {
                "primeira_query": self.metrics[0]['timestamp'],
                "ultima_query": self.metrics[-1]['timestamp'],
                "total_queries": total_queries
            },
            "performance": {
                "queries_bem_sucedidas": successful,
                "queries_com_erro": total_queries - successful - blocked,
                "taxa_sucesso": f"{(successful/total_queries*100):.1f}%"
            },
            "tempo_resposta": {
                "media_segundos": round(statistics.mean(response_times), 2) if response_times else 0,
                "mediana_segundos": round(statistics.median(response_times), 2) if response_times else 0,
                "minimo_segundos": round(min(response_times), 2) if response_times else 0,
                "maximo_segundos": round(max(response_times), 2) if response_times else 0
            },
            "guardrails": {
                "total_bloqueadas": blocked,
                "taxa_bloqueio": f"{(blocked/total_queries*100):.1f}%",
                "economia_estimada_tokens": blocked * 1500,
                "economia_estimada_usd": f"${(blocked * 1500 * 0.375 / 1_000_000):.4f}"
            },
            "distribuicao_queries": type_distribution,
            "analise_por_tipo": analysis_by_type,
            "custos": {
                "total_tokens": total_tokens,
                "custo_total_usd": f"${total_cost:.4f}",
                "custo_medio_por_query": f"${(total_cost/total_queries):.6f}" if total_queries > 0 else "$0"
            }
        }
        
        return summary
    
    def get_detailed_report(self) -> str:
        """Gera relatório detalhado em texto."""
        summary = self.get_summary()
        
        if "error" in summary:
            return summary["error"]
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           RELATÓRIO DE MÉTRICAS - FINSIGHT AI                ║
╚══════════════════════════════════════════════════════════════╝

📅 PERÍODO DE ANÁLISE
   Primeira Query: {summary['periodo']['primeira_query']}
   Última Query:   {summary['periodo']['ultima_query']}
   Total Queries:  {summary['periodo']['total_queries']}

✅ PERFORMANCE
   Bem-sucedidas:  {summary['performance']['queries_bem_sucedidas']}
   Com Erro:       {summary['performance']['queries_com_erro']}
   Taxa de Sucesso: {summary['performance']['taxa_sucesso']}

⚡ TEMPO DE RESPOSTA
   Média:    {summary['tempo_resposta']['media_segundos']}s
   Mediana:  {summary['tempo_resposta']['mediana_segundos']}s
   Mínimo:   {summary['tempo_resposta']['minimo_segundos']}s
   Máximo:   {summary['tempo_resposta']['maximo_segundos']}s

🛡️ GUARDRAILS (Economia)
   Queries Bloqueadas: {summary['guardrails']['total_bloqueadas']}
   Taxa de Bloqueio:   {summary['guardrails']['taxa_bloqueio']}
   Tokens Economizados: ~{summary['guardrails']['economia_estimada_tokens']:,}
   Custo Economizado:   {summary['guardrails']['economia_estimada_usd']}

📊 DISTRIBUIÇÃO DE QUERIES
"""
        for qtype, count in summary['distribuicao_queries'].items():
            percentage = (count / summary['periodo']['total_queries']) * 100
            report += f"   {qtype.upper():12} {count:3} queries ({percentage:.1f}%)\n"
        
        # Análise detalhada por tipo
        if summary.get('analise_por_tipo'):
            report += f"""
📈 ANÁLISE POR TIPO DE QUERY
"""
            for qtype, data in summary['analise_por_tipo'].items():
                report += f"""   {qtype.upper()}:
      Quantidade:    {data['count']} queries
      Tempo Médio:   {data['avg_time']}s
      Total Tokens:  {data['total_tokens']:,}
      Custo Total:   {data['total_cost']}
      Custo Médio:   {data['avg_cost']}
"""
        
        report += f"""
💰 CUSTOS
   Total de Tokens:      {summary['custos']['total_tokens']:,}
   Custo Total:          {summary['custos']['custo_total_usd']}
   Custo Médio/Query:    {summary['custos']['custo_medio_por_query']}

╚══════════════════════════════════════════════════════════════╝
"""
        return report
    
    def export_for_visualization(self, output_file: str = "outputs/metrics_export.json"):
        """Exporta métricas formatadas para visualização."""
        summary = self.get_summary()
        
        export_data = {
            "summary": summary,
            "raw_metrics": self.metrics
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Métricas exportadas para {output_file}")


if __name__ == "__main__":
    collector = MetricsCollector()
    
    print("Simulando queries para teste...\n")
    
    collector.log_query(query="Quantos clientes temos?", query_type="sql", response_time=1.2, tokens_used=850, success=True, sql_query="SELECT COUNT(*) FROM clientes")
    collector.log_query(query="Qual a taxa de juros?", query_type="rag", response_time=0.8, tokens_used=650, success=True)
    collector.log_query(query="Clientes SP na Faixa A?", query_type="hybrid", response_time=2.1, tokens_used=1200, success=True, sql_query="SELECT COUNT(*) FROM clientes WHERE estado = 'SP' AND faixa_risco = 'A'")
    collector.log_query(query="Receita de bolo", query_type="blocked", response_time=0.1, tokens_used=50, success=False, blocked_reason="off-topic")
    
    print(collector.get_detailed_report())
