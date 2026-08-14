import requests
import json
from datetime import date
from s3_writer import upload_to_s3

# Each source has its own web address (API) that returns job listings
SOURCES = {
    "remoteok": "https://remoteok.com/api",
    "arbeitnow": "https://www.arbeitnow.com/api/job-board-api",
}


def fetch_jobs(source_name: str, url: str):
    """
    Calls the API and gets back the raw job data.
    'headers' pretends to be a normal browser, since some APIs
    block requests that don't look like they're from a browser.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # stops here if the request failed
    return response.json()


def save_raw_locally(source_name: str, data):
    """
    Saves the raw data as a .json file on your laptop first,
    before uploading it to S3.
    """
    today = date.today().isoformat()  # e.g. "2026-08-14"
    filename = f"{source_name}_{today}.json"
    with open(filename, "w") as f:
        json.dump(data, f)
    return filename


if __name__ == "__main__":
    today = date.today().isoformat()

    for source_name, url in SOURCES.items():
        print(f"Fetching from {source_name}...")
        data = fetch_jobs(source_name, url)

        local_file = save_raw_locally(source_name, data)
        print(f"Saved locally: {local_file}")

        s3_key = f"raw/source={source_name}/date={today}/{local_file}"
        upload_to_s3(local_file, s3_key)