# 🚀 Projeto Engenharia de Dados (G.E.) – Pipeline ETL com 1 Bilhão de Linhas

Este repositório contém um pipeline ETL de engenharia de dados construído em equipe no contexto do Projeto Orion, do Instituto de Computação da UFAL. O objetivo é simular, armazenar e consultar grandes volumes de dados utilizando ferramentas modernas e uma arquitetura dockerizada.

## 🔧 Tecnologias utilizadas

- **Python + Faker + Polars** – Geração de dados sintéticos realistas
- **MinIO** – Data Lake local (compatível com o Amazon S3)
- **DuckDB** – Armazenamento local em Parquet e validação
- **Trino** – Consulta SQL distribuída sobre arquivos no data lake
- **Hive Metastore + PostgreSQL** – Catálogo de tabelas e metadados
- **Docker + Docker Compose** – Orquestração de todos os serviços

## 📁 Estrutura do projeto

```bash
.
├── data_lake/
│   └── landing-zone/                  # Arquivos .parquet gerados por lote
├── scripts/
│   └── script-gerador.py              # Script de geração em lote
│   └── verificador-amostra-dados.py   # Script para verificar uma amostra dos dados gerados
│   └── verificador-num-linhas         # Script para verificar o total de linhas do dataset
├── docker-compose.yml                 # Orquestração dos serviços
├── log_geracao_dados.txt              # Registro do log de execução do script gerador
└── .gitignore                         # Arquivos e pastas ignorados
```
## ▶️ Como rodar o projeto
1. Clone o repositório:
```bash
git clone https://github.com/maineros/pipeline-1b.git
cd pipeline-1b
```
2. Gere os dados:
```bash
python scripts/script-gerador.py
```
3. Suba os serviços no Docker:
```bash
docker-compose up -d
```
4. Acesse:
- MinIO: http://localhost:9090
- Trino: http://localhost:8080 (Ainda não disponível)

## 📌 Status
- ✔️ Geração de dados
- ✔️ Upload para MinIO
- 🚧 Em breve: Análises com DuckDB
- 🚧 Em breve: Registro de Metadados com Hive Metastore
- 🚧 Em breve: Consulta via Trino

## 📧 Contato
| Nome | E-mail|
|------|-------|
| Laura Mainero | lblrm@ic.ufal.br|
| Leandro Marcio | lmes@ic.ufal.br |
