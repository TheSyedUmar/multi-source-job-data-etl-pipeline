from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text
from typing import Optional

app = FastAPI(title="Multi-Source Job Data API")

DATABASE_URL = "sqlite:///jobs.db"
engine = create_engine(DATABASE_URL)


@app.get("/")
def home():
    """A simple root endpoint, just to confirm the API is alive."""
    return {"message": "Job data API is running. Try /jobs to see listings."}


@app.get("/jobs")
def get_jobs(
    location: Optional[str] = Query(None, description="Filter by location, e.g. 'Remote'"),
    company: Optional[str] = Query(None, description="Filter by company name"),
    limit: int = Query(20, description="Max number of results to return"),
):
    """
    Returns job listings from the database.
    Optional filters: location and company (partial match, case-insensitive).
    """
    query = "SELECT job_title, company, location, source, url FROM jobs WHERE 1=1"
    params = {}

    if location:
        query += " AND location LIKE :location"
        params["location"] = f"%{location}%"

    if company:
        query += " AND company LIKE :company"
        params["company"] = f"%{company}%"

    query += " LIMIT :limit"
    params["limit"] = limit

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        rows = [dict(row._mapping) for row in result]

    return {"count": len(rows), "jobs": rows}