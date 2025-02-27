# OCL Mapper API

This project implements an API that ingests clinical terms from CSV files and matches them against multiple dictionaries (e.g., MSF and CIEL) using a BioBERT-based model. The API returns candidate matches along with confidence scores and is designed for integration with existing OpenConceptLab components.

## Project Overview

The API performs the following tasks:
- **Data Ingestion & Preprocessing:** Loads CSV data and JSON dictionary sources, normalizing multilingual text fields.
- **Embedding & Matching:** Uses BioBERT (or an alternative model) to generate embeddings for clinical terms and dictionary entries. A nearest-neighbor search retrieves candidate matches, which are then scored and categorized.
- **API Layer:** Exposes a RESTful API (using FastAPI) to upload CSV files and return match results in a JSON format suitable for integration with the OCL web UI.
- **User Feedback System**: Allows **manual corrections** via `/feedback` API.
- **Dynamic Score Adjustment**: **Learns over time** and improves match accuracy.
- **Categorized Matches**: Labels results as:
  - ✅ `"Pre-matched"` (High confidence)
  - ⚠ `"To review"` (Medium confidence)
  - ❌ `"No match"` (Low confidence)
- **Swagger UI for Testing**: Easily test endpoints at `http://127.0.0.1:8000/docs`.

## File Structure

```bash
ocl-mapper/
├── data/
│   ├── raw/                     # CSV input files
│   ├── processed/               # Extracted JSON & feedback storage
│   │   ├── OCL_MSF_Source.json  # MSF and CEIL Medical Dictionary
│   │   ├── feedback_store.json  # Stores user feedback (Auto-created)
├── src/
│   ├── ingestion/
│   │   ├── csv_loader.py        # CSV Processing
│   │   ├── json_loader.py       # JSON Parsing (MSF Dictionary)
│   ├── matching/
│   │   ├── matcher.py           # Matching Algorithm with BioBERT
│   ├── model/
│   │   ├── embedder.py          # BioBERT Text Embeddings
│   ├── api/
│   │   ├── app.py               # FastAPI Endpoints
│   ├── utils/
│   │   ├── config.py            # Thresholds & Weights
├── tests/                       # Unit Tests
├── requirements.txt              # Python Dependencies
├── README.md                     # Project Documentation

```

## Prerequisites

- [Python 3.9+](https://www.python.org/downloads/) (if running locally without Docker)


##  Installation & Setup

###  **Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **Run the API**
```bash
uvicorn src.api.app:app --reload
```

### **Test Endpoints in Swagger**
```bash
Go to http://127.0.0.1:8000/docs and try:

/match → Upload a CSV and get matching results.
/feedback → Submit corrections to improve future matches.
```

## How Feedback System Works

1. Run ```/match``` API → Get results with similarity scores.
2. Submit ```/feedbac```k API → Store corrections.
3. Re-run ```/match``` → Corrected terms get a boosted score automatically.

### Example Feedback Submission

```JSON
{
  "term": "loss of interest",
  "correct_match": {
    "candidate_id": "7306178",
    "candidate_text": "depressive symptoms"
  }
}
```

```JSON
{
  "results": [
    {
      "term": "loss of interest",
      "matches": [
        {"candidate_id": "7306178", "candidate_text": "depressive symptoms", "similarity_score": 0.96},
        {"candidate_id": "5687649", "candidate_text": "positive thoughts", "similarity_score": 0.89}
      ]
    }
  ]
}
```