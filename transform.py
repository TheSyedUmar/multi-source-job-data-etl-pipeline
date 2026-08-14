import json
import re
from datetime import date, datetime
import pandas as pd


def clean_html(raw_html: str) -> str:
    """
    Job descriptions come full of HTML tags like <strong>, <p>, <br/>.
    This strips them out so we're left with plain readable text.
    """
    if not raw_html:
        return ""
    clean = re.sub(r"<[^>]+>", " ", raw_html)  # remove anything inside < >
    clean = re.sub(r"\s+", " ", clean).strip()  # collapse extra whitespace
    return clean


def normalize_remoteok(raw_data: list) -> list:
    """
    RemoteOK's first item is a legal notice, not a job — skip it.
    Map RemoteOK's field names to our common schema.
    """
    jobs = []
    for item in raw_data:
        if "position" not in item:  # this skips the legal notice entry
            continue
        jobs.append({
            "source": "remoteok",
            "job_title": item.get("position", "").strip(),
            "company": item.get("company", "").strip(),
            "location": item.get("location", "").strip().rstrip(",").strip() or "Remote",
            "tags": item.get("tags", []),
            "url": item.get("url", ""),
            "description": clean_html(item.get("description", "")),
            "posted_date": datetime.fromtimestamp(item.get("epoch", 0)).date().isoformat() if item.get("epoch") else None,
            "is_remote": True,  # RemoteOK only lists remote jobs
        })
    return jobs


def normalize_arbeitnow(raw_data: dict) -> list:
    """
    Arbeitnow wraps jobs inside a 'data' key.
    Map Arbeitnow's field names to our common schema.
    """
    jobs = []
    items = raw_data.get("data", [])
    for item in items:
        jobs.append({
            "source": "arbeitnow",
            "job_title": item.get("title", "").strip(),
            "company": item.get("company_name", "").strip(),
            "location": item.get("location", "").strip() or "Remote",
            "tags": item.get("tags", []),
            "url": item.get("url", ""),
            "description": clean_html(item.get("description", "")),
            "posted_date": datetime.fromtimestamp(item.get("created_at", 0)).date().isoformat() if item.get("created_at") else None,
            "is_remote": item.get("remote", False),
        })
    return jobs


def deduplicate(jobs: list) -> list:
    """
    Removes duplicate job postings, using the job's URL as the
    unique fingerprint (two jobs are 'the same' if they have the same URL).
    """
    seen_urls = set()
    unique_jobs = []
    for job in jobs:
        if job["url"] not in seen_urls:
            seen_urls.add(job["url"])
            unique_jobs.append(job)
    return unique_jobs


if __name__ == "__main__":
    today = date.today().isoformat()

    with open(f"remoteok_{today}.json") as f:
        remoteok_raw = json.load(f)

    with open(f"arbeitnow_{today}.json") as f:
        arbeitnow_raw = json.load(f)

    remoteok_jobs = normalize_remoteok(remoteok_raw)
    arbeitnow_jobs = normalize_arbeitnow(arbeitnow_raw)

    print(f"RemoteOK: {len(remoteok_jobs)} jobs parsed")
    print(f"Arbeitnow: {len(arbeitnow_jobs)} jobs parsed")

    all_jobs = remoteok_jobs + arbeitnow_jobs
    unique_jobs = deduplicate(all_jobs)

    print(f"Total before dedup: {len(all_jobs)}")
    print(f"Total after dedup: {len(unique_jobs)}")

    df = pd.DataFrame(unique_jobs)
    output_file = f"processed_jobs_{today}.parquet"
    df.to_parquet(output_file, index=False)
    print(f"Saved cleaned data to {output_file}")

    print("\nSample of cleaned data:")
    print(df[["source", "job_title", "company", "location"]].head(5))
    from s3_writer import upload_to_s3
    s3_processed_key = f"processed/date={today}/{output_file}"
    upload_to_s3(output_file, s3_processed_key)