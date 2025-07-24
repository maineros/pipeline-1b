import duckdb
import pandas as pd

# Esse é o caminho para acessar os arquivos Parquet 
parquet_path = 'data_lake/landing-zone/*.parquet'

# Aqui vamos nos conectar com o DuckBD
con = duckdb.connect()

# CONSULTA: Total de linhas
total_linhas = con.execute(f"SELECT COUNT(*) FROM '{parquet_path}'").fetchone()[0]
print(f"Total de linhas no dataset: {total_linhas:,}")

# CONSULTA: valores mínimos, médios e máximos das transações realizadas

estatisticas = con.execute(f"""
    SELECT 
        ROUND(AVG(transaction_amount), 2) AS media,
        MIN(transaction_amount) AS minimo,
        MAX(transaction_amount) AS maximo
    FROM '{parquet_path}'
""").fetchdf()
print("\nEstatísticas de valor das transações:")
print(estatisticas)

# CONSULTA: Transaçoes por método de pagamento

pagamentos = con.execute(f"""
    SELECT 
        payment_method, 
        COUNT(*) AS total, 
        ROUND(AVG(transaction_amount), 2) AS media_valor
    FROM '{parquet_path}'
    GROUP BY payment_method
    ORDER BY total DESC
""").fetchdf()
print("\nTransações por método de pagamento:")
print(pagamentos)

# CONSULTA: Transações por categoria de comercio 

categorias = con.execute(f"""
    SELECT 
        merchant_category, 
        COUNT(*) AS total_transacoes,
        ROUND(AVG(transaction_amount), 2) AS media_valor
    FROM '{parquet_path}'
    GROUP BY merchant_category
    ORDER BY total_transacoes DESC
""").fetchdf()
print("\nTransações por categoria de comércio:")
print(categorias)

# CONSULTA: A tendência mensal de transações

tendencia = con.execute(f"""
    SELECT 
        DATE_TRUNC('month', transaction_date) AS mes,
        COUNT(*) AS total_transacoes,
        ROUND(SUM(transaction_amount), 2) AS total_valor
    FROM '{parquet_path}'
    GROUP BY mes
    ORDER BY mes
""").fetchdf()
print("\nTendência mensal de transações:")
print(tendencia)

# CONSULTA: top 10 clientes por gasto 

top_clientes = con.execute(f"""
    SELECT 
        customer_id, 
        ROUND(SUM(transaction_amount), 2) AS total_gasto
    FROM '{parquet_path}'
    GROUP BY customer_id
    ORDER BY total_gasto DESC
    LIMIT 10
""").fetchdf()
print("\nTop 10 clientes por gasto:")
print(top_clientes)

# Valor médio das transações por cliente e método de pagamento
media_cliente_pagamento = con.execute(f"""
    SELECT 
        customer_id,
        payment_method,
        ROUND(AVG(transaction_amount), 2) AS media_valor
    FROM '{parquet_path}'
    GROUP BY customer_id, payment_method
    ORDER BY media_valor DESC
    LIMIT 20
""").fetchdf()
print("\nTop 20 combinações cliente x método de pagamento por valor médio:")
print(media_cliente_pagamento)

# Clientes com maior número de transações acima da média global

media_global = estatisticas['media'][0]

clientes_acima_media = con.execute(f"""
    SELECT 
        customer_id,
        COUNT(*) AS transacoes_acima_media
    FROM '{parquet_path}'
    WHERE transaction_amount > {media_global}
    GROUP BY customer_id
    ORDER BY transacoes_acima_media DESC
    LIMIT 10
""").fetchdf()
print("\nTop 10 clientes com mais transações acima da média global:")
print(clientes_acima_media)

# Categoria com maior crescimento de transações mês a mês

crescimento_categoria = con.execute(f"""
    WITH transacoes_mes AS (
        SELECT 
            DATE_TRUNC('month', transaction_date) AS mes,
            merchant_category,
            COUNT(*) AS total_mes
        FROM '{parquet_path}'
        GROUP BY mes, merchant_category
    ),
    crescimento AS (
        SELECT 
            t1.merchant_category,
            t1.mes,
            t1.total_mes,
            (t1.total_mes - t2.total_mes) AS variacao
        FROM transacoes_mes t1
        LEFT JOIN transacoes_mes t2
        ON t1.merchant_category = t2.merchant_category
           AND t1.mes = DATE_ADD('month', 1, t2.mes)
    )
    SELECT * 
    FROM crescimento
    ORDER BY variacao DESC
    LIMIT 10
""").fetchdf()
print("\nCategorias com maior crescimento mensal de transações:")
print(crescimento_categoria)

# Frequência média de transações por cliente (dias entre compras)

frequencia_clientes = con.execute(f"""
    SELECT 
        customer_id,
        ROUND(AVG(DATEDIFF('day', LAG(transaction_date) OVER (PARTITION BY customer_id ORDER BY transaction_date), transaction_date)), 2) AS media_dias
    FROM '{parquet_path}'
    QUALIFY COUNT(*) OVER (PARTITION BY customer_id) > 1
""").fetchdf()
print("\nMédia de dias entre compras por cliente:")
print(frequencia_clientes.head(10))

# Detectar possíveis fraudes: múltiplas transações de alto valor no mesmo dia por cliente

fraudes_potenciais = con.execute(f"""
    SELECT 
        customer_id,
        transaction_date::DATE AS data,
        COUNT(*) AS transacoes_alto_valor,
        SUM(transaction_amount) AS total_dia
    FROM '{parquet_path}'
    WHERE transaction_amount > 1000  -- valor arbitrário, ajuste conforme o contexto
    GROUP BY customer_id, data
    HAVING COUNT(*) >= 3
    ORDER BY transacoes_alto_valor DESC, total_dia DESC
""").fetchdf()
print("\nClientes com múltiplas transações de alto valor no mesmo dia (potencial fraude):")
print(fraudes_potenciais)



# OPCIONAL
# Salvar em CSV (valores separados por vírgulas) cujo objetivo é armazenar dados em forma de tabela onde cada linha é um registro e cada coluna é separada por vírgulas

analise_dir = "scripts/resultados"
import os
os.makedirs(analise_dir, exist_ok=True)

pagamentos.to_csv(f"{analise_dir}/pagamentos.csv", index=False)
categorias.to_csv(f"{analise_dir}/categorias.csv", index=False)
tendencia.to_csv(f"{analise_dir}/tendencia_mensal.csv", index=False)
top_clientes.to_csv(f"{analise_dir}/top_clientes.csv", index=False)
media_cliente_pagamento.to_csv(f"{analise_dir}/media_cliente_pagamento.csv", index=False)
clientes_acima_media.to_csv(f"{analise_dir}/clientes_acima_media.csv", index=False)
crescimento_categoria.to_csv(f"{analise_dir}/crescimento_categoria.csv", index=False)
frequencia_clientes.to_csv(f"{analise_dir}/frequencia_clientes.csv", index=False)
fraudes_potenciais.to_csv(f"{analise_dir}/fraudes_potenciais.csv", index=False)

print("\nResultados salvos em 'scripts/resultados/'")



