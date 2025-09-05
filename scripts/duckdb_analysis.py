import duckdb
import pandas as pd

# Esse é o caminho para acessar os arquivos Parquet 
parquet_path = 'data_lake/staging/*.parquet'

# Conexão com DuckDB
con = duckdb.connect()

# =========================
# Funções de Análise
# =========================

def contar_linhas(con, path):
    return con.execute(f"SELECT COUNT(*) FROM '{path}'").fetchone()[0]

def estatisticas_transacoes(con, path):
    return con.execute(f"""
        SELECT 
            ROUND(AVG(transaction_amount), 2) AS media,
            MIN(transaction_amount) AS minimo,
            MAX(transaction_amount) AS maximo
        FROM '{path}'
    """).fetchdf()

def transacoes_por_metodo_pagamento(con, path):
    return con.execute(f"""
        SELECT 
            payment_method, 
            COUNT(*) AS total, 
            ROUND(AVG(transaction_amount), 2) AS media_valor
        FROM '{path}'
        GROUP BY payment_method
        ORDER BY total DESC
    """).fetchdf()

def transacoes_por_categoria(comercio_con, path):
    return comercio_con.execute(f"""
        SELECT 
            merchant_category, 
            COUNT(*) AS total_transacoes,
            ROUND(AVG(transaction_amount), 2) AS media_valor
        FROM '{path}'
        GROUP BY merchant_category
        ORDER BY total_transacoes DESC
    """).fetchdf()

def tendencia_mensal(con, path):
    return con.execute(f"""
        SELECT 
            DATE_TRUNC('month', transaction_date) AS mes,
            COUNT(*) AS total_transacoes,
            ROUND(SUM(transaction_amount), 2) AS total_valor
        FROM '{path}'
        GROUP BY mes
        ORDER BY mes
    """).fetchdf()

def top_10_clientes_por_gasto(con, path):
    return con.execute(f"""
        SELECT 
            customer_id, 
            ROUND(SUM(transaction_amount), 2) AS total_gasto
        FROM '{path}'
        GROUP BY customer_id
        ORDER BY total_gasto DESC
        LIMIT 10
    """).fetchdf()

def media_por_cliente_e_pagamento(con, path):
    return con.execute(f"""
        SELECT 
            customer_id,
            payment_method,
            ROUND(AVG(transaction_amount), 2) AS media_valor
        FROM '{path}'
        GROUP BY customer_id, payment_method
        ORDER BY media_valor DESC
        LIMIT 20
    """).fetchdf()

def clientes_acima_media(con, path, media_global):
    return con.execute(f"""
        SELECT 
            customer_id,
            COUNT(*) AS transacoes_acima_media
        FROM '{path}'
        WHERE transaction_amount > {media_global}
        GROUP BY customer_id
        ORDER BY transacoes_acima_media DESC
        LIMIT 10
    """).fetchdf()

def crescimento_categoria_mes(con, path):
    return con.execute(f"""
        WITH transacoes_mes AS (
            SELECT 
                DATE_TRUNC('month', transaction_date) AS mes,
                merchant_category,
                COUNT(*) AS total_mes
            FROM '{path}'
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

def frequencia_media_clientes(con, path):
    return con.execute(f"""
        SELECT 
            customer_id,
            ROUND(AVG(DATEDIFF('day', 
                LAG(transaction_date) OVER (PARTITION BY customer_id ORDER BY transaction_date), 
                transaction_date)), 2) AS media_dias
        FROM '{path}'
        QUALIFY COUNT(*) OVER (PARTITION BY customer_id) > 1
    """).fetchdf()

def detectar_fraudes(con, path):
    return con.execute(f"""
        SELECT 
            customer_id,
            transaction_date::DATE AS data,
            COUNT(*) AS transacoes_alto_valor,
            SUM(transaction_amount) AS total_dia
        FROM '{path}'
        WHERE transaction_amount > 1000
        GROUP BY customer_id, data
        HAVING COUNT(*) >= 3
        ORDER BY transacoes_alto_valor DESC, total_dia DESC
    """).fetchdf()
