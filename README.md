\# Multi-Source Job Data ETL/ELT Pipeline with AWS S3 Data Lake



An end-to-end data engineering pipeline that scrapes job listings from multiple external sources, lands raw data in an AWS S3 data lake, transforms and normalizes inconsistent schemas, loads cleaned data into a database, and exposes it through a REST API.



\## Problem this solves



Job listings are scattered across different websites, each with its own data format. This pipeline automates collecting, cleaning, and unifying listings from multiple sources into one consistent, queryable dataset.



\## Architecture
Scrape (2 sources) → Land raw in S3 → Transform \& clean → Land processed in S3 → Load to database → Serve via API

Raw data is always landed in S3 \*\*before\*\* any cleaning happens. This is the core ETL/ELT design decision in this project: if the transform logic has a bug, it can be re-run against the untouched raw data without re-scraping the source websites.



\## Pipeline stages



\### 1. Scrape (`scraper.py`)

Fetches job listings from two sources:

\- \[RemoteOK](https://remoteok.com) API

\- \[Arbeitnow](https://www.arbeitnow.com) API



\### 2. Land raw data in S3 (`s3\_writer.py`)

Raw JSON is uploaded to S3, partitioned by source and date:
s3://bucket/raw/source=remoteok/date=2026-08-17/remoteok\_2026-08-17.json

s3://bucket/raw/source=arbeitnow/date=2026-08-17/arbeitnow\_2026-08-17.json



!\[S3 raw folder structure](screenshots/s3-raw-folder.png)

!\[S3 raw file detail](screenshots/s3-raw-file-detail.png)



\### 3. Transform (`transform.py`)

Each source has a completely different schema (e.g. RemoteOK uses `position`, Arbeitnow uses `title`). This stage:

\- Normalizes both sources into one common schema

\- Strips HTML tags from job descriptions

\- Removes trailing formatting artifacts (e.g. trailing commas in location fields)

\- Deduplicates listings by URL



!\[Transform and load output](screenshots/transform-output.png)



\### 4. Land processed data in S3

Cleaned data is saved as Parquet and uploaded separately:
s3://bucket/processed/date=2026-08-17/processed\_jobs\_2026-08-17.parquet
!\[S3 processed folder structure](screenshots/s3-processed-folder.png)



\### 5. Load to database (`load\_to\_db.py`)

Cleaned data is loaded into a SQLite database for fast querying.



\### 6. Serve via API (`main.py`)

A FastAPI service exposes the cleaned data with filterable endpoints:
GET /jobs?location=Remote

GET /jobs?company=Google
!\[API response](screenshots/api-response.png)



\## Tech stack



\- \*\*Python\*\* — core pipeline logic

\- \*\*requests / BeautifulSoup\*\* — data ingestion

\- \*\*pandas\*\* — data cleaning and normalization

\- \*\*AWS S3 (boto3)\*\* — data lake storage, raw/processed zone separation

\- \*\*SQLite (SQLAlchemy)\*\* — structured storage for queries

\- \*\*FastAPI\*\* — REST API layer



\## Running it locally



```bash

\# 1. Set up environment

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt



\# 2. Add AWS credentials to a .env file

AWS\_ACCESS\_KEY\_ID=your\_key

AWS\_SECRET\_ACCESS\_KEY=your\_secret

AWS\_REGION=ap-south-1

BUCKET\_NAME=your-bucket-name



\# 3. Run the pipeline

python scraper.py       # scrape + land raw in S3

python transform.py     # clean + land processed in S3

python load\_to\_db.py    # load into database



\# 4. Start the API

uvicorn main:app --reload

```



\## Commit history



!\[Commit history](screenshots/commit-history.png)



\## Known limitations



\- Deduplication matches on exact URL only — near-duplicate reposts of the same role under different URLs are not currently caught

\- Two sources are used; a third, HTML-based source (rather than JSON API) would further demonstrate parsing of unstructured data

\- No orchestration layer (e.g. Airflow) — pipeline stages are run sequentially via individual scripts



\## What this project demonstrates



\- Multi-source data ingestion via scraping and APIs

\- Schema normalization across heterogeneous data sources

\- ETL/ELT pattern with a proper raw/processed data lake separation on S3

\- Structured data loading and API exposure

