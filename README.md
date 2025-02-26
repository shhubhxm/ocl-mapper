# OCL Mapper API

This project implements an API that ingests clinical terms from CSV files and matches them against multiple dictionaries (e.g., MSF and CIEL) using a BioBERT-based model. The API returns candidate matches along with confidence scores and is designed for integration with existing OpenConceptLab components.

## Project Overview

The API performs the following tasks:
- **Data Ingestion & Preprocessing:** Loads CSV data and JSON dictionary sources, normalizing multilingual text fields.
- **Embedding & Matching:** Uses BioBERT (or an alternative model) to generate embeddings for clinical terms and dictionary entries. A nearest-neighbor search retrieves candidate matches, which are then scored and categorized.
- **API Layer:** Exposes a RESTful API (using FastAPI) to upload CSV files and return match results in a JSON format suitable for integration with the OCL web UI.
- **Docker Integration:** The entire application is containerized using Docker, ensuring a consistent runtime environment and simplifying deployment.

## File Structure

```
ocl-mapper/
├── data/
│   ├── raw/
│   │   ├── MSF_MentalHealth_Concepts_Benchmarking_Dataset.csv
│   │   └── OCL_MSF_Source_v20250224.zip
│   └── processed/
├── models/
│   └── BioBERT/                # Local model files and configuration
├── src/
│   ├── ingestion/
│   │   ├── csv_loader.py       # CSV ingestion and preprocessing module
│   │   └── json_loader.py      # JSON parsing for MSF and CIEL sources
│   ├── matching/
│   │   └── matcher.py          # Candidate retrieval and scoring logic
│   ├── api/
│   │   └── app.py              # FastAPI endpoints for file upload and matching
│   ├── model/
│   │   └── embedder.py         # BioBERT loading and embedding generation
│   └── utils/
│       └── config.py           # Configuration parameters (thresholds, weights)
├── tests/                      # Unit tests for all modules
├── Dockerfile                  # Dockerfile for containerizing the API
├── docker-compose.yml          # docker-compose for simplified deployment
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview, setup, and usage instructions
└── setup.sh                    # Script to setup the project environment
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (and optionally docker-compose)
- [Python 3.9+](https://www.python.org/downloads/) (if running locally without Docker)

## Installation & Setup

### Running with Docker

1. **Build the Docker Image:**
   ```bash
   docker build -t ocl-mapper-api .
Run the Container:

bash
Copy
docker run -p 8000:8000 ocl-mapper-api
Alternatively, if using docker-compose:

bash
Copy
docker-compose up --build
Access the API: The API will be available at http://localhost:8000. Use tools like Postman or the integrated UI to upload CSV files and retrieve match results.

Running Locally (Without Docker)
Create a Virtual Environment:

bash
Copy
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
Install Dependencies:

bash
Copy
pip install --upgrade pip
pip install -r requirements.txt
Run the API:

bash
Copy
uvicorn src.api.app:app --reload
The API will be available at http://localhost:8000.