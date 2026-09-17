# Sydney Solutions Consulting Job Market Intelligence

An end-to-end data engineering and analytics project that collects, processes, stores and analyses job-market data for Solutions Consultant, Solutions Engineer, Sales Engineer and Pre-Sales roles in Sydney, Australia.

The project was built to demonstrate a complete data pipeline from API ingestion through to data transformation, relational storage, analytical SQL and dashboard visualisation.

## Project Overview

The objective is to answer questions such as:

* How many relevant roles are currently available in Sydney?
* Which companies are hiring the most?
* Which technical and commercial skills are most frequently requested?
* How active is the market over time?
* Which current opportunities are the strongest fit for my background?
* How can this data be refreshed without manually rebuilding the analysis?

The current version uses a transparent, rules-based approach to job-skill extraction and job-fit scoring. A future version can extend this into an AI-powered job classification and recommendation system.

---

## Architecture

```text
                 ┌─────────────────────┐
                 │     Adzuna API      │
                 │   Sydney job data   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │       Python        │
                 │                     │
                 │ • API ingestion     │
                 │ • Pagination        │
                 │ • Deduplication     │
                 │ • Data cleaning     │
                 │ • Skill extraction  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │     PostgreSQL      │
                 │                     │
                 │ • jobs              │
                 │ • job_skills        │
                 │ • analytical views  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │      Metabase       │
                 │                     │
                 │ • KPIs              │
                 │ • Market trends     │
                 │ • Skills analysis   │
                 │ • Hiring companies  │
                 │ • Recent jobs       │
                 │ • Job-fit analysis  │
                 └─────────────────────┘
```

---

## Data Source

Job listings are retrieved from the Adzuna Jobs API.

The pipeline searches across multiple relevant job titles:

* Solutions Consultant
* Solution Consultant
* Solutions Engineer
* Sales Engineer
* Pre-Sales Consultant
* Pre-Sales Engineer
* Technical Solutions Consultant

The searches are restricted to **Sydney, Australia**.

Each search is paginated so that multiple result pages can be retrieved where available. Results from the different searches are subsequently deduplicated using the Adzuna job ID.

---

## Technology Stack

| Component               | Technology            |
| ----------------------- | --------------------- |
| Data source             | Adzuna API            |
| Programming             | Python                |
| Data processing         | Pandas                |
| API requests            | Requests              |
| Configuration           | python-dotenv         |
| Database                | PostgreSQL            |
| Database connectivity   | SQLAlchemy / psycopg2 |
| Analytics               | SQL                   |
| Visualisation           | Metabase              |
| Containerisation        | Docker                |
| Development environment | macOS                 |

---

## Data Pipeline

### 1. Ingestion

`dataingestion.py` connects to the Adzuna API using credentials stored in environment variables.

API credentials are deliberately not stored in the source code.

```text
ADZUNA_APP_ID
ADZUNA_APP_KEY
```

The pipeline executes multiple searches against the Sydney job market and retrieves available listings.

### 2. Pagination

Each search is processed page-by-page rather than relying on a single API request.

This allows the pipeline to retrieve a larger set of available listings.

### 3. Deduplication

The same job can appear under multiple search terms.

For example, a role could match both:

```text
Solutions Consultant
```

and

```text
Solution Consultant
```

Jobs are therefore deduplicated using the unique Adzuna job ID before being loaded into the database.

### 4. Data Cleaning

The raw API response is transformed into a consistent relational structure containing fields such as:

* Job ID
* Title
* Company
* Location
* Description
* Created date
* Minimum salary
* Maximum salary
* Contract type
* Contract time
* Category
* Job URL
* Last seen timestamp

### 5. Skill Extraction

A rule-based skill extraction layer scans job descriptions for relevant technologies and capabilities.

The current skill taxonomy includes areas such as:

* SQL
* Python
* AWS
* Azure
* GCP
* APIs
* Databricks
* Snowflake
* Power BI
* Tableau
* SaaS
* Pre-Sales
* Discovery
* Demonstrations
* Solution Design
* Solution Architecture
* Integration
* Data Analytics
* Artificial Intelligence
* Machine Learning
* Fintech
* Financial Services

Extracted skills are stored separately from the main job table using a many-to-many relationship.

---

## Database Design

### `jobs`

The primary job listing table.

```text
jobs
├── job_id
├── title
├── company
├── location
├── description
├── created
├── salary_min
├── salary_max
├── contract_time
├── contract_type
├── category
├── job_url
└── last_seen_at
```

### `job_skills`

Stores the relationship between jobs and extracted skills.

```text
job_skills
├── job_id
└── skill
```

The primary key is:

```text
(job_id, skill)
```

This prevents the same skill from being associated with the same job more than once.

---

## Data Persistence

The pipeline uses PostgreSQL upserts rather than replacing the entire dataset during every run.

This means previously discovered jobs can remain in the database while new ingestion runs update existing records.

The `last_seen_at` field records when a job was most recently encountered by the pipeline.

This creates the foundation for future historical analysis of job availability and market movement.

---

## Analytical SQL Views

Several PostgreSQL views were created to separate analytical logic from the raw data.

### `vw_job_market_summary`

Provides headline market KPIs including:

* Total jobs
* Jobs posted in the last 7 days
* Jobs posted in the last 30 days
* Companies hiring
* Average salary information
* Jobs with disclosed salary
* Salary coverage
* Latest job posted

### `vw_top_skills`

Aggregates extracted skills by the number of distinct jobs requiring each skill.

This provides a view of the technical and commercial capabilities most frequently requested by employers.

### `vw_recent_jobs`

Provides a focused view of recently posted roles.

### `vw_job_fit`

Calculates a rules-based fit score for each job.

The current scoring model rewards the presence of capabilities such as:

| Capability                     | Weight |
| ------------------------------ | -----: |
| SQL                            |     10 |
| Python                         |     10 |
| Databricks / Snowflake         |     10 |
| APIs / Integration             |     10 |
| Pre-Sales                      |     15 |
| Discovery                      |     10 |
| Demonstrations                 |     10 |
| Solution Design / Architecture |     10 |
| Data Analytics / AI / ML       |     10 |
| Fintech / Financial Services   |      5 |

The resulting score is capped at 100.

The scoring model is intentionally transparent rather than presenting the output as a machine-learning probability.

---

## Dashboard

The Metabase dashboard provides a market-level view of Sydney's Solutions Consulting and technical sales market.

### Key Performance Indicators

* Total Jobs
* Jobs Last 7 Days
* Companies Hiring
* Salary Coverage

### Market Activity

**Jobs Over Time**

Shows job posting activity over time.

### Skills

**Top Skills**

Shows the technologies, capabilities and domain knowledge most frequently identified in job descriptions.

### Employers

**Top Hiring Companies**

Ranks companies by the number of relevant roles identified.

### Opportunities

**Recent Jobs**

Provides the latest relevant job listings.

### Personalised Analysis

**Best Fit Jobs**

Ranks opportunities according to the rules-based fit score.

This turns the dashboard from a purely descriptive market report into an actionable job-search tool.

---

## One-Click Refresh

The project includes a Mac launcher:

```text
refresh_data.command
```

This allows the data pipeline to be refreshed without manually typing the Python command into Terminal.

The underlying process remains:

```text
Adzuna API
     ↓
Python ingestion
     ↓
Data cleaning
     ↓
Skill extraction
     ↓
PostgreSQL upsert
     ↓
Metabase refresh
```

The project can therefore be refreshed as new jobs become available.

---

## Current V1 Results

A recent pipeline execution demonstrated the end-to-end workflow successfully.

The latest run:

* Queried 7 different job-title searches
* Retrieved results from the Adzuna API
* Deduplicated overlapping listings
* Extracted job skills
* Loaded jobs into PostgreSQL
* Loaded extracted skills into PostgreSQL
* Successfully updated the analytical data used by Metabase

The database verification returned:

```text
Total jobs:              148
Jobs in last 7 days:      20
Jobs with extracted skills: 34
```

These figures will change as the pipeline is refreshed.

---

## Data Quality & Limitations

This project is deliberately a V1 implementation and has several known limitations.

### Job descriptions

The availability and completeness of job descriptions depends on the source data returned by the API. In some cases descriptions may be truncated, which can cause relevant skills to be missed.

### Skill extraction

The current extraction process is keyword-based.

For example, the pipeline currently looks for explicit occurrences of terms such as `python`, `sql` and `snowflake`.

This approach is transparent and easy to understand but can produce:

* False positives
* False negatives
* Missed synonyms
* Missed contextual requirements

A future NLP-based approach would improve this.

### Salary data

Salary information is not available for every listing.

Salary metrics should therefore be interpreted alongside salary coverage rather than as a representative market-wide salary.

### Job freshness

`created` represents the advertised job creation date supplied by the source.

`last_seen_at` records when the pipeline most recently encountered the listing.

A future version can introduce `first_seen_at` to distinguish jobs newly discovered by the pipeline from jobs that were already known.

---

## Future Development — V2

The next version of the project will move beyond keyword matching towards intelligent job classification.

Potential V2 architecture:

```text
                  Job Description
                         ↓
                  AI Classification
                         ↓
              ┌─────────────────────┐
              │ Structured Job Data │
              │                     │
              │ Role type           │
              │ Seniority           │
              │ Technical skills    │
              │ Cloud technologies   │
              │ Pre-sales intensity │
              │ Industry            │
              │ Requirements        │
              └──────────┬──────────┘
                         ↓
                  Candidate Profile
                         ↓
                  Intelligent Fit
                         ↓
              Score + Explanation
```

Potential V2 capabilities include:

* LLM-based job classification
* Improved skill taxonomy
* Semantic job matching
* Personalised fit explanations
* Seniority matching
* Identification of skill gaps
* Automated daily ingestion
* Job alerts
* Historical market analysis
* Cloud deployment
* AI-generated application recommendations

---

## Project Objective

This project demonstrates an end-to-end approach to building a practical data product:

**Ingest → Transform → Store → Analyse → Visualise → Act**

Rather than analysing a static dataset, the system is designed around a continuously changing real-world data source and provides a practical analytical application on top of it.

The project also provides a foundation for demonstrating data engineering, SQL, Python, analytics, data modelling and eventually AI/ML capabilities in a single portfolio project.
