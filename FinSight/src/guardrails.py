from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class FinSightGuardrails:
    """Mecanismo de segurança para filtrar queries inadequadas."""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        system_prompt = """Você é um filtro de segurança para o FinSight, um assistente de análise de risco de crédito.

O FinSight responde perguntas sobre:
- Risco de crédito e dados financeiros
- Scores, rendas e informações de clientes
- Políticas de crédito e taxas de juros
- Consultas sobre dados de clientes no banco de dados
- Análises estatísticas de carteira de clientes

Você deve bloquear APENAS:
1. Linguagem ofensiva ou agressiva (xingamentos, palavrões)
2. Temas polêmicos sem relação com finanças (política, religião, etc)
3. Perguntas completamente fora do contexto financeiro (história, geografia, ciência não relacionada)

IMPORTANTE: Perguntas sobre dados de clientes, estatísticas, scores e análises financeiras devem ser PERMITIDAS.

Se a pergunta for segura e minimamente relacionada ao contexto de análise de crédito/dados financeiros, responda apenas: "ALLOWED"

Se precisar bloquear, responda educadamente explicando brevemente o motivo.

Exemplos:
- "Qual a taxa para score 600?" → ALLOWED
- "Quantos clientes temos?" → ALLOWED
- "Quantos clientes temos no RJ?" → ALLOWED
- "Qual a média de renda dos clientes?" → ALLOWED
- "Me mostre os dados, seu idiota" → "Por favor, mantenha um tom respeitoso."
- "O que você acha do governo atual?" → "Minha especialidade é análise financeira, não opino sobre política."
- "Quando foi a revolução francesa?" → "Sou especializado em análise de crédito e dados financeiros."
"""

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def check_input(self, user_input: str) -> str:
        """Valida se o input é apropriado. Retorna 'ALLOWED' ou mensagem de bloqueio."""
        return self.chain.invoke({"input": user_input})
