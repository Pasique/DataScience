# Sistema de Recomendação Híbrido com PySpark

> Um estudo comparativo completo implementando e avaliando três abordagens de sistemas de recomendação: Filtragem Colaborativa (ALS), Sistema Baseado em Conteúdo e uma estratégia Híbrida.

## 🎯 Objetivo

Este projeto demonstra o desenvolvimento end-to-end de sistemas de recomendação escaláveis, comparando diferentes paradigmas e suas métricas de performance para identificar a melhor estratégia de implementação.

## 📊 Principais Resultados

- **Sistema Híbrido** superou ambos os métodos isolados em **todas as métricas**
- **NDCG@10: 0.8089** (competitivo com state-of-the-art)
- **Precision@10: 57.14%** vs 56.02% (ALS) e 52.55% (Content-Based)
- **RMSE < 1.0** demonstrando excelente capacidade preditiva

## 🏗️ Arquitetura do Sistema

### 1. Filtragem Colaborativa (ALS)
- Algoritmo: Alternating Least Squares
- Força: Captura padrões latentes complexos
- Limitação: Cold start e sparsity

### 2. Sistema Baseado em Conteúdo
- Técnica: TF-IDF com similaridade cosseno
- Força: Funciona com poucos dados
- Limitação: Restrito à similaridade explícita

### 3. Sistema Híbrido
- Combinação linear dos scores (ALS + Content-Based)
- Parâmetro alpha configurável
- Mitiga limitações de ambos os sistemas

## 🛠️ Stack Tecnológica

**Core:**
- PySpark (Processamento distribuído)
- Apache Spark MLlib
- Python 3.x

**Bibliotecas:**
- NumPy (Computação numérica)
- Pandas (Manipulação de dados)
- Matplotlib (Visualização)

**Algoritmos:**
- ALS (Alternating Least Squares)
- TF-IDF (Term Frequency-Inverse Document Frequency)
- Similaridade Cosseno