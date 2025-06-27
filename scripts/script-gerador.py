import polars as pl
from faker import Faker
import random
from datetime import datetime
import os

fake = Faker()
Faker.seed(42)
random.seed(42)

# teste local com menor quantidade de linhas (10_000_000)
BATCH_SIZE = 100_000
NUM_BATCHES = 100

# 1 bilhao de linhas (1_000_000_000) 
# BATCH_SIZE = 10_000_000 # tamanho de cada lote
# NUM_BATCHES = 100

# categorias ficticias
merchant_categories = ['food', 'electronics', 'clothing', 'transport', 'health']

payment_methods = ['credit_card', 'debit_card', 'pix', 'paypal', 'boleto']

# geracao de lote
def gerar_lote(batch_num):
    print(f"Gerando lote {batch_num+1}/{NUM_BATCHES}...")
    return pl.DataFrame({
    
        "transaction_id": [f"{batch_num}_{i}" for i in range(BATCH_SIZE)],
        "customer_id": [fake.uuid4() for _ in range(BATCH_SIZE)],
        "transaction_amount": [round(random.uniform(10, 1000), 2) for _ in range(BATCH_SIZE)],
        "transaction_date": [
            fake.date_time_between(start_date='-1y', end_date='now') for _ in range(BATCH_SIZE)
        ],
        "merchant_category": [random.choice(merchant_categories) for _ in range(BATCH_SIZE)],
        "payment_method": [random.choice(payment_methods) for _ in range(BATCH_SIZE)]
    })

# salvar em vários arquivos parquet (um por lote)
os.makedirs("data_lake/landing-zone", exist_ok=True)

for i in range(NUM_BATCHES):
    df = gerar_lote(i)
    path = f"data_lake/landing-zone/transactions_batch_{i}.parquet"
    df.write_parquet(path)
    print(f"Lote {i+1} salvo em {path}")

    # ADD: registrar no arquivo de log pra manter o tracking da execucao do script
    # inicialmente, para testes: se o script for interrompido, saberemos a partir de onde retomar
    with open("log_geracao_dados.txt", "a") as log_file:
        log_file.write(f"{datetime.now()} - Lote {i+1}/{NUM_BATCHES} salvo em {path}\n")
