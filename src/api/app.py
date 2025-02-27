from fastapi import FastAPI, UploadFile, File, HTTPException
import json
import os
from src.ingestion.csv_loader import load_csv
from src.ingestion.json_loader import load_json
from src.matching.matcher import Matcher

app = FastAPI(title="OCL Mapper API")

# ✅ Load real dictionary concepts
json_file_path = "data/raw/export.json"
concepts_data = load_json(json_file_path)

# ✅ Load stored feedback (if exists)
feedback_file = "data/processed/feedback_store.json"

def load_feedback():
    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

feedback_store = load_feedback()

# ✅ Build candidates from the dictionary
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

candidate_texts, candidate_ids = build_candidates_from_dict(concepts_data)

# ✅ Initialize matcher
matcher = Matcher(candidate_texts, candidate_ids)

# ✅ Categorize Matches
def categorize_match(score):
    if score >= 0.99:
        return "Pre-matched"
    elif 0.75 <= score < 0.99:
        return "To review"
    else:
        return "No match"

@app.post("/match")
async def match_terms(file: UploadFile = File(...)):
    contents = await file.read()
    with open("temp.csv", "wb") as f:
        f.write(contents)
    df = load_csv("temp.csv")

    results = []
    if "Label" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV missing 'Label' column")

    for term in df["Label"].dropna():
        match_result = matcher.match(term, top_k=3)

        for match in match_result:
            match["category"] = categorize_match(match["similarity_score"])

        results.append({"term": term, "matches": match_result})

    return {"results": results}

# ✅ Feedback API to Store User Validation
@app.post("/feedback")
async def store_feedback(feedback: dict):
    """
    Stores user feedback on matches in a local JSON file.
    """
    term = feedback.get("term")
    correct_match = feedback.get("correct_match")

    if not term or not correct_match:
        raise HTTPException(status_code=400, detail="Missing 'term' or 'correct_match' in feedback.")

    if term not in feedback_store:
        feedback_store[term] = []

    feedback_store[term].append(correct_match)

    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(feedback_store, f, indent=4)

    return {"message": "Feedback stored successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
