from fastapi import FastAPI, UploadFile, File, HTTPException
from src.ingestion.csv_loader import load_csv
from src.ingestion.json_loader import load_json
from src.matching.matcher import Matcher

app = FastAPI(title="OCL Mapper API")

# loading json
json_file_path = "data/raw/export.json"
try:
    concepts_data = load_json(json_file_path)
except Exception as e:
    raise RuntimeError(f"❌ Error loading JSON: {e}")

# extracting candidate names & IDs from JSON
def build_candidates_from_dict(concepts_data):
    candidate_texts = []
    candidate_ids = []
    
    for concept in concepts_data:
        if "display_name" in concept:
            candidate_texts.append(concept["display_name"].lower().strip())
            candidate_ids.append(concept["uuid"])

        if "names" in concept:
            for name_entry in concept["names"]:
                if "name" in name_entry:
                    candidate_texts.append(name_entry["name"].lower().strip())
                    candidate_ids.append(concept["uuid"])

    return candidate_texts, candidate_ids

# loading candidates
try:
    candidate_texts, candidate_ids = build_candidates_from_dict(concepts_data)
    matcher = Matcher(candidate_texts, candidate_ids)
except Exception as e:
    raise RuntimeError(f"❌ Error initializing matcher: {e}")

@app.post("/match")
async def match_terms(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open("temp.csv", "wb") as f:
            f.write(contents)
        df = load_csv("temp.csv")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV: {e}")

    if "Label" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV missing 'Label' column")

    results = []
    for term in df["Label"].dropna():
        match_result = matcher.match(term, top_k=3)
        results.append({"term": term, "matches": match_result})

    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
