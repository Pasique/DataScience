import sqlite3
import os
from faker import Faker
import random
from datetime import datetime, timedelta
import numpy as np

# Configurações
DB_NAME = "../data/credit_risk.db"
NUM_CLIENTES = 500  # Tamanho da amostra
SEED = 42

# Inicialização
fake = Faker('pt_BR')
Faker.seed(SEED)
random.seed(SEED)
np.random.seed(SEED)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = 1") # Habilita integridade referencial
    return conn

def create_schema(conn):
    cursor = conn.cursor()
    
    # Drop tables para garantir idempotência (em dev)
    cursor.executescript("""
        DROP TABLE IF EXISTS tb_pagamentos;
        DROP TABLE IF EXISTS tb_operacoes;
        DROP TABLE IF EXISTS tb_scores;
        DROP TABLE IF EXISTS tb_clientes;
    """)
    
    # Criação das tabelas
    # Design Pattern: Chaves Surrogadas (id autoincrement) vs Chaves Naturais (CPF).
    # Escolha: Surrogadas para performance e desacoplamento.
    
    cursor.executescript("""
        CREATE TABLE tb_clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            data_nascimento DATE,
            renda_mensal REAL,
            estado TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE tb_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            data_referencia DATE,
            score INTEGER CHECK(score >= 0 AND score <= 1000),
            FOREIGN KEY (id_cliente) REFERENCES tb_clientes(id)
        );

        CREATE TABLE tb_operacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            valor_solicitado REAL,
            taxa_juros REAL,
            prazo_meses INTEGER,
            data_contratacao DATE,
            status TEXT CHECK(status IN ('ATIVA', 'QUITADA', 'WO')),
            FOREIGN KEY (id_cliente) REFERENCES tb_clientes(id)
        );

        CREATE TABLE tb_pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_operacao INTEGER,
            numero_parcela INTEGER,
            data_vencimento DATE,
            data_pagamento DATE,
            valor_parcela REAL,
            status TEXT CHECK(status IN ('PAGO', 'ATRASO', 'PENDENTE')),
            FOREIGN KEY (id_operacao) REFERENCES tb_operacoes(id)
        );
    """)
    conn.commit()
    print("Schema criado com sucesso.")

def generate_data(conn):
    cursor = conn.cursor()
    
    print(f"Gerando {NUM_CLIENTES} clientes...")
    
    clientes = []
    scores = []
    operacoes = []
    pagamentos = []
    
    for _ in range(NUM_CLIENTES):
        # 1. Gerar Cliente
        perfil = fake.profile()
        renda = round(np.random.lognormal(mean=8.5, sigma=0.8), 2) # Distribuição Log-normal para renda (mais realista)
        if renda < 1300: renda = 1300 # Salário mínimo aprox
        
        cliente = (
            fake.name(),
            fake.cpf(),
            perfil['birthdate'],
            renda,
            fake.state_abbr()
        )
        cursor.execute("INSERT INTO tb_clientes (nome, cpf, data_nascimento, renda_mensal, estado) VALUES (?, ?, ?, ?, ?)", cliente)
        id_cliente = cursor.lastrowid
        
        # 2. Gerar Score (Correlacionado com Renda + Ruído Aleatório)
        # Renda maior tende a ter score maior, mas não garantido
        base_score = min(1000, int((renda / 20) + random.randint(300, 600)))
        score_final = max(0, min(1000, base_score + random.randint(-100, 100)))
        
        cursor.execute("INSERT INTO tb_scores (id_cliente, data_referencia, score) VALUES (?, ?, ?)", 
                       (id_cliente, datetime.now().date(), score_final))
        
        # 3. Gerar Operações (Apenas para alguns clientes)
        if random.random() > 0.3: # 70% dos clientes têm operações
            
            # Regra de Negócio Simulada: Score define taxa e limite
            if score_final >= 850:
                taxa = random.uniform(1.5, 2.5)
                limite_multiplicador = 10
            elif score_final >= 700:
                taxa = random.uniform(2.6, 4.0)
                limite_multiplicador = 5
            elif score_final >= 500:
                taxa = random.uniform(4.1, 6.0)
                limite_multiplicador = 2
            else:
                taxa = random.uniform(8.0, 12.0) # Alto risco
                limite_multiplicador = 0.5
            
            valor_solicitado = round(random.uniform(1000, renda * limite_multiplicador), 2)
            prazo = random.choice([12, 24, 36, 48])
            data_contratacao = fake.date_between(start_date='-2y', end_date='today')
            
            # Simples cálculo de parcela (Price)
            i = taxa / 100
            valor_parcela = round((valor_solicitado * i) / (1 - (1 + i)**(-prazo)), 2)
            
            status_op = 'ATIVA'
            
            cursor.execute("""
                INSERT INTO tb_operacoes (id_cliente, valor_solicitado, taxa_juros, prazo_meses, data_contratacao, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_cliente, valor_solicitado, taxa, prazo, data_contratacao, status_op))
            id_operacao = cursor.lastrowid
            
            # 4. Gerar Pagamentos
            # Simular comportamento de pagamento baseado no Score
            prob_atraso = 0.05 if score_final > 800 else (0.30 if score_final < 500 else 0.15)
            
            data_base = data_contratacao
            for n in range(1, prazo + 1):
                data_venc = data_base + timedelta(days=30*n)
                
                if data_venc > datetime.now().date():
                    status_pag = 'PENDENTE'
                    data_pag = None
                else:
                    # Passado
                    if random.random() < prob_atraso:
                        status_pag = 'ATRASO'
                        # Alguns pagam com atraso, outros nunca pagam (Default)
                        if random.random() > 0.5:
                            data_pag = data_venc + timedelta(days=random.randint(5, 90))
                            status_pag = 'PAGO' # Pagou com atraso
                        else:
                            data_pag = None # Continua em atraso
                    else:
                        status_pag = 'PAGO'
                        data_pag = data_venc
                
                cursor.execute("""
                    INSERT INTO tb_pagamentos (id_operacao, numero_parcela, data_vencimento, data_pagamento, valor_parcela, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (id_operacao, n, data_venc, data_pag, valor_parcela, status_pag))

    conn.commit()
    print("Dados gerados com sucesso.")

if __name__ == "__main__":
    # Muda para o diretório raiz do projeto se estiver em scripts
    if os.path.basename(os.getcwd()) == "scripts":
        os.chdir("..")
    
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    
    conn = get_db_connection()
    create_schema(conn)
    generate_data(conn)
    conn.close()
