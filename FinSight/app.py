import streamlit as st
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent import get_agent, guardrails
from metrics import MetricsCollector

if "metrics_collector" not in st.session_state:
    st.session_state.metrics_collector = MetricsCollector()

st.set_page_config(page_title="FinSight AI", page_icon="💰", layout="wide")

st.title("💰 FinSight AI Assistant")
st.markdown("""
Assistente especializado em **Análise de Risco de Crédito**. Faça perguntas sobre dados de clientes,
políticas de risco ou análises combinadas.
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    with st.spinner("Carregando agente..."):
        st.session_state.agent = get_agent()

with st.sidebar:
    st.header("💡 Exemplos de Perguntas")
    
    if st.button("📊 Quantos clientes temos em SP?"):
        st.session_state.example_query = "Quantos clientes temos em SP?"
    
    if st.button("💰 Taxa para score 650?"):
        st.session_state.example_query = "Qual a taxa de juros para um cliente com score 650?"
    
    if st.button("🎯 Clientes Faixa A no RJ?"):
        st.session_state.example_query = "Quantos clientes da Faixa A temos no Rio de Janeiro?"
    
    st.divider()
    st.header("⚙️ Sistema")
    
    st.markdown("""
    **Stack Técnica:**
    - LangGraph (orquestração)
    - RAG com ChromaDB
    - SQL Agent
    - Guardrails customizado
    """)
    
    if st.button("📊 Ver Métricas"):
        st.session_state.show_metrics = True
    
    if st.button("🗑️ Limpar Chat"):
        st.session_state.messages = []
        st.rerun()

# Modal de métricas
if "show_metrics" in st.session_state and st.session_state.show_metrics:
    summary = st.session_state.metrics_collector.get_summary()
    
    if "error" in summary:
        st.info(summary["error"])
        if st.button("Fechar"):
            st.session_state.show_metrics = False
            st.rerun()
    else:
        # KPIs principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queries", summary["periodo"]["total_queries"])
            st.metric("Taxa Sucesso", summary["performance"]["taxa_sucesso"])
        
        with col2:
            st.metric("Tempo Médio", f"{summary['tempo_resposta']['media_segundos']}s")
            st.metric("Mediana", f"{summary['tempo_resposta']['mediana_segundos']}s")
        
        with col3:
            st.metric("Bloqueadas", summary["guardrails"]["total_bloqueadas"])
            st.metric("Taxa Bloqueio", summary["guardrails"]["taxa_bloqueio"])
        
        with col4:
            st.metric("Custo Total", summary["custos"]["custo_total_usd"])
            st.metric("Custo/Query", summary["custos"]["custo_medio_por_query"])
        
        st.divider()
        
        # Distribuição e análise por tipo
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Distribuição")
            st.json(summary["distribuicao_queries"])
        
        with col_right:
            st.subheader("Economia Guardrails")
            st.success(f"Tokens: ~{summary['guardrails']['economia_estimada_tokens']:,}")
            st.success(f"Custo: {summary['guardrails']['economia_estimada_usd']}")
        
        # Análise detalhada por tipo
        if "analise_por_tipo" in summary and summary["analise_por_tipo"]:
            st.divider()
            st.subheader("Análise por Tipo")
            
            for qtype, data in summary["analise_por_tipo"].items():
                with st.expander(f"{qtype.upper()} - {data['count']} queries"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Tempo Médio", f"{data['avg_time']}s")
                    with c2:
                        st.metric("Tokens", f"{data['total_tokens']:,}")
                    with c3:
                        st.metric("Custo Médio", data['avg_cost'])
        
        if st.button("Fechar Métricas"):
            st.session_state.show_metrics = False
            st.rerun()

# Exibir histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Processar query de exemplo se houver
if "example_query" in st.session_state:
    prompt = st.session_state.example_query
    del st.session_state.example_query
    st.rerun()
else:
    prompt = None

# Input do usuário
if not prompt:
    prompt = st.chat_input("Digite sua pergunta...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    start_time = time.time()
    query_type = None
    success = True
    error_msg = None
    
    with st.chat_message("assistant"):
        # Placeholder para resposta
        message_placeholder = st.empty()
        
        # 1. Guardrails Check
        is_safe = False
        with st.status("🛡️ Verificando Guardrails...", expanded=False) as status:
            check_result = guardrails.check_input(prompt)
            if check_result != "ALLOWED":
                status.update(label="🚫 Bloqueado pelo Guardrails", state="error")
                response = f"🚫 **Bloqueado**: {check_result}"
                message_placeholder.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Log métrica de bloqueio
                response_time = time.time() - start_time
                st.session_state.metrics_collector.log_query(
                    query=prompt,
                    query_type="blocked",
                    response_time=response_time,
                    tokens_used=50,
                    success=False,
                    blocked_reason=check_result,
                    sql_query=None
                )
            else:
                status.update(label="✅ Input Seguro e Relevante", state="complete")
                is_safe = True

        # 2. Agent Execution (apenas se passou no guardrails)
        if is_safe:
            with st.spinner("🤖 Analisando dados e políticas..."):
                try:
                    inputs = {"messages": [("user", prompt)]}
                    result = st.session_state.agent.invoke(inputs)
                    response = result["messages"][-1].content
                    
                    message_placeholder.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Detecta tipo de query baseado nas tools usadas pelo agente e extrai SQL
                    used_sql = False
                    used_rag = False
                    sql_query = None
                    
                    for msg in result["messages"]:
                        msg_content = str(msg).lower()
                        if any(term in msg_content for term in ["sql_db", "list_tables", "query_sql"]):
                            used_sql = True
                            # Tenta extrair query SQL
                            if "select" in msg_content:
                                import re
                                sql_pattern = r"(SELECT\s+.*?)(?:;|\n|$|'|\")"
                                matches = re.findall(sql_pattern, str(msg), re.IGNORECASE | re.DOTALL)
                                if matches:
                                    sql_query = matches[0].strip()
                        if any(term in msg_content for term in ["search_policy", "glossary", "política"]):
                            used_rag = True
                    
                    if used_sql and used_rag:
                        query_type = "hybrid"
                    elif used_sql:
                        query_type = "sql"
                    elif used_rag:
                        query_type = "rag"
                    else:
                        query_type = "unknown"
                    
                    # Estimativa mais precisa de tokens (OpenAI usa ~1.3 tokens por palavra)
                    prompt_tokens = int(len(prompt.split()) * 1.3)
                    response_tokens = int(len(response.split()) * 1.3)
                    tokens_used = (prompt_tokens + response_tokens) * 2  # Fator para mensagens de sistema e contexto
                    
                except Exception as e:
                    success = False
                    error_msg = str(e)
                    query_type = "error"
                    tokens_used = 100
                    
                    error_response = f"❌ Ocorreu um erro ao processar sua solicitação: {error_msg}"
                    message_placeholder.error(error_response)
                    st.session_state.messages.append({"role": "assistant", "content": error_response})
                
                # Log métrica de query executada
                response_time = time.time() - start_time
                st.session_state.metrics_collector.log_query(
                    query=prompt,
                    query_type=query_type or "unknown",
                    response_time=response_time,
                    tokens_used=tokens_used,
                    success=success,
                    error=error_msg,
                    sql_query=sql_query if 'sql_query' in locals() else None
                )
