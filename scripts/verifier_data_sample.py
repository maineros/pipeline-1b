import duckdb

con = duckdb.connect()

df = con.execute("SELECT * FROM 'data_lake/landing-zone/transactions_batch_0.parquet' LIMIT 10").fetchdf()
print(df)