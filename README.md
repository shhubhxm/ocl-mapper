# OCL Mapper API

This FastAPI-powered medical terminology matching system uses BioBERT embeddings to find the most relevant medical concepts based on semantic similarity. Given a term from a CSV file, the system generates an embedding and compares it against a structured medical dictionary (CIEL/MSF dataset) to find the closest match using cosine similarity.

To improve the accuracy of results, the system integrates with Supabase, a cloud-based PostgreSQL database, where users can provide feedback corrections. This feedback adjusts future similarity calculations, ensuring that validated matches always appear as the top result for the given term.

**Author:** **𝕊𝕙𝕦𝕓𝕙𝕒𝕞 𝕍𝕪𝕒𝕤**   ([GitHub](https://github.com/shhubhxm) | [Email](mailto:vyasshubham.41@gmail.com))

# Project Overview

## Features
- **Medical Concept Matching**: Matches terms from a CSV file to concepts in the MSF dictionary.
- **BioBERT-based Embeddings**: Uses **`dmis-lab/biobert-base-cased-v1.1`** to generate embeddings for accurate similarity-based matching.
- **Real-time Feedback System**: Stores **user corrections** in **Supabase** and dynamically updates results.
- **Supabase Cloud Storage**: Stores feedback in a **PostgreSQL cloud database**, eliminating file-based issues.
- **Dynamic Score Adjustment**: **Learns over time** and **ensures corrected matches always appear**.
- **API with FastAPI & Uvicorn**: Provides easy-to-use RESTful endpoints.
- **Swagger UI for Testing**: Easily test endpoints at `http://127.0.0.1:8000/docs`.

---

## Project Structure
```
ocl-mapper/
├── data/
│   ├── raw/                     # CSV input files
│   │   ├── MSF.csv              # Benchmarking CSV
│   ├── processed/               # Extracted JSON & feedback storage
│   │   ├── export.json          # Medical Dictionary
├── src/
│   ├── ingestion/
│   │   ├── csv_loader.py        # CSV Processing
│   │   ├── json_loader.py       # JSON Parsing (MSF Dictionary)
│   ├── matching/
│   │   ├── matcher.py           # Matching Algorithm with BioBERT
│   ├── model/
│   │   ├── embedder.py          # BioBERT Text Embeddings
│   ├── api/
│   │   ├── app.py               # FastAPI Endpoints with Supabase Integration
│   ├── utils/
│   │   ├── config.py            # Thresholds & Weights
├── tests/                       # Unit Tests
├── requirements.txt              # Python Dependencies
├── README.md                     # Project Documentation
```

---

## Installation & Setup

### **1. Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Set Up Supabase**
- Create an account at **[https://supabase.com](https://supabase.com)**
- Create a **new project**
- Go to **"Table Editor"** → Create a table **`feedback_store`**
- Add these columns:
   
   | Column Name       | Type        | Default |
   |------------------|------------|----------|
   | `id`            | `uuid` (Primary Key) | `gen_random_uuid()` |
   | `term`          | `TEXT`      | |
   | `candidate_id`  | `TEXT`      | |
   | `candidate_text`| `TEXT`      | |

- Copy **Supabase URL** & **API Key**
- Add these to your `.env` file:
   ```bash
   SUPABASE_URL="https://your-supabase-url.supabase.co"
   SUPABASE_KEY="your-supabase-secret-key"
   ```

### **3. Run the API**
```bash
uvicorn src.api.app:app --reload
```

### **4. Test Endpoints in Swagger**
Go to **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** and try:
- **`/match`** → Upload a CSV and get matching results.
- **`/feedback`** → Submit corrections to improve future matches.

---

##  **How the Feedback System Works**
1. **Run `/match` API** → Get results with similarity scores.
2. **Submit `/feedback` API** → Store corrections **in Supabase**.
3. **Re-run `/match`** → **Corrected terms** will be the **only match displayed**.

---

### **Example Feedback Submission**
**Request to `/feedback`:**
```json
{
  "term": "some (-3 points)",
  "correct_match": {
    "candidate_id": "5756853",
    "candidate_text": "feels like they have failed someone"
  }
}
```

**Supabase Database (`feedback_store` table) After Insertion:**
| term            | candidate_id | candidate_text                      |
|----------------|-------------|-------------------------------------|
| some (-3 points) | 5756853      | feels like they have failed someone |

---

### **Example Updated Matching Output**
After submitting feedback, running `/match` will return:
```json
{
  "results": [
    {
      "term": "some (-3 points)",
      "matches": [
        {"candidate_id": "5756853", "candidate_text": "feels like they have failed someone", "similarity_score": 1.0, "adjusted_by_feedback": true}
      ]
    }
  ]
}
```
**Feedback ensures only the corrected match appears!** 

---

## **Troubleshooting**
- **API Not Loading?** Restart with:
  ```bash
  uvicorn src/api.app:app --reload
  ```
- **Feedback Not Updating?**  
  - Run **this SQL query in Supabase** to check stored feedback:
    ```sql
    SELECT * FROM public.feedback_store WHERE term = 'some (-3 points)';
    ```
  - If the row is missing, `/feedback` did not save data correctly.
  - If the row exists but does not appear in `/match`, restart the API.
---