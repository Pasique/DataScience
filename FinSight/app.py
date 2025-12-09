import streamlit as st
import os
import sys

# Adiciona o diretório atual ao path para garantir que as importações funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import get_agent, guardrails

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
    
    if st.button("Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()

# Exibir mensagens anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do usuário
if prompt := st.chat_input("Digite sua pergunta (ex: Qual a taxa para score 600? ou Quantos clientes em SP?)"):
    # Adicionar mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
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
