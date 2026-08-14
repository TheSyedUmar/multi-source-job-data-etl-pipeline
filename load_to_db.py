import pandas as pd
from sqlalchemy import create_engine
from datetime import date

DATABASE_URL = "sqlite:///jobs.db"  # creates a file called jobs.db in this folder

engine = create_engine(DATABASE_URL)


def load_parquet_to_db(parquet_file: str, table_name: str = "jobs"):
    """
    Reads the cleaned Parquet file and loads it into a database table.
    if_exists='replace' means: each time this runs, wipe the old table
    and put the fresh data in. Fine for now since we're not appending
    daily yet — just proving the load step works.
    """
    df = pd.read_parquet(parquet_file)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into '{table_name}' table in {DATABASE_URL}")


if __name__ == "__main__":
    today = date.today().isoformat()
    parquet_file = f"processed_jobs_{today}.parquet"
    load_parquet_to_db(parquet_file)

    # Quick sanity check: read a few rows back to confirm it worked
    check_df = pd.read_sql("SELECT job_title, company, location FROM jobs LIMIT 5", engine)
    print("\nSample from database:")
    print(check_df)