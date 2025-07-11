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

# OPCIONAL
# Salvar em CSV (valores separados por vírgulas) cujo objetivo é armazenar dados em forma de tabela onde cada linha é um registro e cada coluna é separada por vírgulas

analise_dir = "scripts/resultados"
import os
os.makedirs(analise_dir, exist_ok=True)

pagamentos.to_csv(f"{analise_dir}/pagamentos.csv", index=False)
categorias.to_csv(f"{analise_dir}/categorias.csv", index=False)
tendencia.to_csv(f"{analise_dir}/tendencia_mensal.csv", index=False)
top_clientes.to_csv(f"{analise_dir}/top_clientes.csv", index=False)

print("\nResultados salvos em 'scripts/resultados/'")



