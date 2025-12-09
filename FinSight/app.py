import streamlit as st
import os
import sys
import time

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent import get_agent, guardrails
from metrics import MetricsCollector

# Inicializar coletor de métricas
if "metrics_collector" not in st.session_state:
    st.session_state.metrics_collector = MetricsCollector()

st.set_page_config(page_title="FinSight AI", page_icon="💰", layout="wide")

st.title("💰 FinSight AI Assistant")
st.markdown("""
Seu assistente especialista em **Risco de Crédito** e **Análise Financeira**.
Pergunte sobre dados de clientes, políticas de risco ou faça análises complexas.
""")

# Inicializar Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    with st.spinner("Inicializando agente..."):
        st.session_state.agent = get_agent()

# Sidebar com informações
with st.sidebar:
    st.header("Sobre")
    st.markdown("""
    Este assistente utiliza:
    - **LangChain & LangGraph** para orquestração.
    - **RAG (ChromaDB)** para consulta de políticas.
    - **SQL Agent** para consulta de dados estruturados.
    - **Guardrails** para segurança e moderação.
    """)
    
    st.divider()
    
    # Botão de métricas
    if st.button("📊 Ver Métricas do Sistema"):
        st.session_state.show_metrics = True
    
    if st.button("Limpar Conversa"):
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
        
# Input do usuário
if prompt := st.chat_input("Digite sua pergunta (ex: Qual a taxa para score 600? ou Quantos clientes em SP?)"):
    # Adicionar mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Processamento
    start_time = time.time()
    query_type = None
    success = True
    error_msg = None
    blocked_reason = None
    
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
                    blocked_reason=check_result
                )
            else:
                status.update(label="✅ Input Seguro e Relevante", state="complete")
                is_safe = True

        # 2. Agent Execution (apenas se passou no guardrails)
        if is_safe:
            with st.spinner("🤖 Analisando dados e políticas..."):
                try:
                    # O agente do LangGraph espera um dicionário com a chave "messages"
                    inputs = {"messages": [("user", prompt)]}
                    
                    # Invoke do agente
                    result = st.session_state.agent.invoke(inputs)
                    
                    # A resposta final é a última mensagem da lista
                    response = result["messages"][-1].content
                    
                    message_placeholder.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Detectar tipo de query
                    response_lower = response.lower()
                    if "select" in response_lower or "database" in response_lower or "sql" in response_lower:
                        query_type = "sql"
                    elif "política" in response_lower or "glossário" in response_lower or "faixa" in response_lower:
                        query_type = "rag"
                    else:
                        query_type = "hybrid"
                    
                    # Estimativa de tokens
                    tokens_used = len(prompt.split()) * 1.3 + len(response.split()) * 1.3
                    tokens_used = int(tokens_used * 100)
                    
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
                    error=error_msg
                )
        st.markdown(prompt)

    # Processamento
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
            else:
                status.update(label="✅ Input Seguro e Relevante", state="complete")
                is_safe = True

        # 2. Agent Execution (apenas se passou no guardrails)
        if is_safe:
            with st.spinner("🤖 Analisando dados e políticas..."):
                try:
                    # O agente do LangGraph espera um dicionário com a chave "messages"
                    inputs = {"messages": [("user", prompt)]}
                    
                    # Invoke do agente
                    result = st.session_state.agent.invoke(inputs)
                    
                    # A resposta final é a última mensagem da lista
                    response = result["messages"][-1].content
                    
                    message_placeholder.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"❌ Ocorreu um erro ao processar sua solicitação: {str(e)}"
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
