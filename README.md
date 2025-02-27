# OCL Mapper API

This project implements an API that ingests clinical terms from CSV files and matches them against multiple dictionaries (e.g., MSF and CIEL) using a BioBERT-based model. The API returns candidate matches along with confidence scores and is designed for integration with existing OpenConceptLab components.

## Project Overview

### **API Functionality (with Exact Libraries & Techniques Used)**  

The API is built using **FastAPI** and leverages **BioBERT embeddings** from `dmis-lab/biobert-base-cased-v1.1` for clinical term matching.  

### **Key Features & Libraries Used:**  

- **Data Ingestion & Preprocessing** (`pandas`, `json`)  
  - Loads CSV files and medical dictionaries (`OCL_MSF_Source.json`).
  - Normalizes multilingual text fields, including **Arabic** (handled as raw text).  

- **Embedding & Matching** (`transformers`, `torch`, `scikit-learn`)  
  - Uses **BioBERT** to generate embeddings for medical terms.  
  - **Cosine similarity (`sklearn.metrics.pairwise.cosine_similarity`)** ranks the best matches.  

- **API Layer** (`fastapi`, `uvicorn`)  
  - **`/match`** → Uploads CSV & returns **top-k concept matches**.  
  - **`/feedback`** → Stores user corrections dynamically in `feedback_store.json`.  

- **Learning from User Feedback** (`json`)  
  - **Feedback improves similarity scores** in real-time.  
  - Reloads feedback dynamically inside `match()` without restarting API.  

- **Categorized Matches**  
  - ✅ **Pre-matched** (High confidence, ≥0.99)  
  - ⚠ **To review** (Medium confidence, 0.75 - 0.99)  
  - ❌ **No match** (Low confidence, <0.75)  

- **Testing & Validation** (`Swagger UI`, `cURL`, `Postman`)  
  - Easily test endpoints at `http://127.0.0.1:8000/docs`.  

### **📌 Summary of Libraries Used**
| **Feature** | **Libraries Used** |
|------------|-----------------|
| **API Development** | `fastapi`, `uvicorn` |
| **Data Handling** | `pandas`, `json`, `os` |
| **Text Embeddings** | `transformers`, `torch` |
| **Similarity Matching** | `scikit-learn (cosine_similarity)`, `numpy` |
| **Multilingual Support** | `langdetect`, `bert-base-multilingual-cased` |
| **Feedback Storage** | `json` (local file-based learning) |

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

- [Python 3.9+]

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
2. Submit ```/feedback``` API → Store corrections.
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