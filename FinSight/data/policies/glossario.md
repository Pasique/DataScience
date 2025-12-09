# Glossário de Termos - FinSight

## Entidades de Dados

*   **Cliente (tb_clientes):** Indivíduo que possui relacionamento com a instituição. Identificado por `id_cliente`.
*   **Score (tb_scores):** Pontuação numérica que representa a probabilidade de inadimplência. Atualizado mensalmente.
*   **Operação (tb_operacoes):** Contrato de empréstimo ou financiamento ativo ou quitado.
*   **Pagamento (tb_pagamentos):** Registro de cada parcela paga ou devida de uma operação.

## Métricas de Negócio

*   **Inadimplência (Default):** Ocorrência de atraso superior a 90 dias no pagamento de uma parcela.
*   **Taxa de Juros (Interest Rate):** Percentual cobrado sobre o valor principal emprestado.
*   **IOF:** Imposto sobre Operações Financeiras (não modelado explicitamente nas tabelas, mas embutido no Custo Efetivo Total).
*   **LTV (Loan-to-Value):** Razão entre o valor do empréstimo e a garantia (não aplicável para crédito pessoal sem garantia).
*   **DTI (Debt-to-Income):** Razão entre as dívidas mensais e a renda bruta do cliente. Usado para validar a regra de 30%.

## Status de Operação
*   **ATIVA:** Empréstimo em curso, pagamentos em dia ou atraso leve.
*   **QUITADA:** Todas as parcelas foram pagas.
*   **WO (Write-Off):** Operação dada como prejuízo contábil após atraso prolongado (> 360 dias).
