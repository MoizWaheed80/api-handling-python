# Dynamic API to SQL Server Data Pipeline

A Python-based data pipeline that extracts product data from an authenticated API, handles pagination, dynamically detects schema changes, normalizes API data, and loads the results into SQL Server.

The project is designed to simulate a real-world API data ingestion workflow.

---

## Project Overview

This project demonstrates how to build a reliable API data pipeline using Python.

The pipeline:

1. Authenticates with the API
2. Extracts data using pagination
3. Processes data in Python
4. Detects new API fields automatically
5. Handles missing API fields without breaking the pipeline
6. Converts nested API objects/lists into JSON
7. Creates the SQL Server table dynamically
8. Loads the processed data into SQL Server
9. Handles errors at each major pipeline stage
10. Runs automatically every 24 hours

---

## Architecture

API
↓
Authentication
↓
Pagination
↓
Extraction
↓
Schema Detection
↓
Normalization
↓
Pandas DataFrame
↓
SQL Server
↓
Products Table

---

## Technologies

- Python
- Requests
- Pandas
- SQLAlchemy
- PyODBC
- SQL Server
- Windows Authentication
- Python-dotenv

---

## Project Structure

```text
dynamic-api-to-sql-pipeline/
│
├── src/
│   ├── main.py
│   ├── config.py
│   ├── api_client.py
│   ├── extractor.py
│   ├── normalizer.py
│   ├── schema_manager.py
│   └── sql_data_push.py
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── venv/
