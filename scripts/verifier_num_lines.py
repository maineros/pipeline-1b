import polars as pl
import os

total_linhas = 0
for i in range(100): # seria o NUM_BATCHES
    path = f"data_lake/landing-zone/transactions_batch_{i}.parquet"
    if os.path.exists(path):
        df = pl.read_parquet(path)
        print(f"{path}: {df.shape[0]} linhas")
        total_linhas += df.shape[0]
    else:
        print(f"{path} não encontrado!")

print(f"Total de linhas somadas: {total_linhas}")
