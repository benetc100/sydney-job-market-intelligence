# 1. Imports
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timezone
from sqlalchemy import create_engine, text

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

url = "https://api.adzuna.com/v1/api/jobs/au/search/1"

search_terms = [
    "solutions consultant",
    "solution consultant",
    "solutions engineer",
    "sales engineer",
    "pre-sales consultant",
    "pre-sales engineer",
    "technical solutions consultant"
]

all_jobs = []

for search_term in search_terms:

    page = 1

    while True:

        url = f"https://api.adzuna.com/v1/api/jobs/au/search/{page}"

        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "title_only": search_term,
            "where": "Sydney",
            "results_per_page": 50
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        results = data["results"]

        print(
            f"{search_term} - page {page}: "
            f"{len(results)} jobs returned"
        )

        # No more jobs = stop paging
        if not results:
            break

        all_jobs.extend(results)

        # If fewer than 50 came back,
        # we've reached the last page
        if len(results) < 50:
            break

        page += 1

df = pd.json_normalize(all_jobs)

df = df.drop_duplicates(subset="id")

print(df.head())
print(df.columns)

##skils optomisation

skills = [
    "sql",
    "python",
    "aws",
    "azure",
    "gcp",
    "api",
    "databricks",
    "snowflake",
    "power bi",
    "tableau",
    "saas",
    "pre-sales",
    "presales",
    "discovery",
    "demo",
    "solution design",
    "solution architecture",
    "integration",
    "data analytics",
    "artificial intelligence",
    "machine learning",
    "fintech",
    "financial services"
]


## we are now cleaning that data 

clean_df = df[[
    "id",
    "title",
    "company.display_name",
    "location.display_name",
    "description",
    "created",
    "salary_min",
    "salary_max",
    "contract_time",
    "contract_type",
    "category.label",
    "redirect_url"
]].copy()

## rename the data

clean_df.columns = [
    "job_id",
    "title",
    "company",
    "location",
    "description",
    "created",
    "salary_min",
    "salary_max",
    "contract_time",
    "contract_type",
    "category",
    "job_url"
]

job_skills = []

for _, row in clean_df.iterrows():
    description = str(row["description"]).lower()

    for skill in skills:
        if skill in description:
            job_skills.append({
                "job_id": row["job_id"],
                "skill": skill
            })


job_skills_df = pd.DataFrame(job_skills)

job_skills_upsert_sql = text("""
    INSERT INTO job_skills (
        job_id,
        skill
    )
    VALUES (
        :job_id,
        :skill
    )
    ON CONFLICT (job_id, skill)
    DO NOTHING;
""")

print(job_skills_df.head())
print(job_skills_df.shape)

print(clean_df.head())
print(clean_df.shape)



clean_df["created"] = pd.to_datetime(clean_df["created"])

# 4. Add ingestion metadata
clean_df["last_seen_at"] = datetime.now(timezone.utc)

print(clean_df.isnull().sum())
print(clean_df["created"].min())
print(clean_df["created"].max())
print(clean_df["title"].value_counts().head(20))


print(clean_df.duplicated(subset="job_id").sum())

clean_df = clean_df.drop_duplicates(subset="job_id")

clean_df.to_csv("jobs_clean.csv", index=False)

## I am now adding this to enable us to connect to the postgres database 

from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://postgres:carry0n123@localhost:5433/job_market"
)

upsert_sql = text("""
    INSERT INTO jobs (
        job_id,
        title,
        company,
        location,
        description,
        created,
        salary_min,
        salary_max,
        contract_time,
        contract_type,
        category,
        job_url,
        last_seen_at
    )
    VALUES (
        :job_id,
        :title,
        :company,
        :location,
        :description,
        :created,
        :salary_min,
        :salary_max,
        :contract_time,
        :contract_type,
        :category,
        :job_url,
        :last_seen_at
    )
    ON CONFLICT (job_id)
    DO UPDATE SET
        title = EXCLUDED.title,
        company = EXCLUDED.company,
        location = EXCLUDED.location,
        description = EXCLUDED.description,
        created = EXCLUDED.created,
        salary_min = EXCLUDED.salary_min,
        salary_max = EXCLUDED.salary_max,
        contract_time = EXCLUDED.contract_time,
        contract_type = EXCLUDED.contract_type,
        category = EXCLUDED.category,
        job_url = EXCLUDED.job_url,
        last_seen_at = EXCLUDED.last_seen_at;
""")

with engine.begin() as connection:
    for _, row in clean_df.iterrows():
        connection.execute(
            upsert_sql,
            row.to_dict()
        )

print("Jobs upserted successfully")


with engine.begin() as connection:
    for _, row in job_skills_df.iterrows():
        connection.execute(
            job_skills_upsert_sql,
            row.to_dict()
        )

print("Job skills loaded successfully")
