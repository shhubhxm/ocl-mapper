from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import json
from supabase import create_client, Client
from src.ingestion.csv_loader import load_csv
from src.ingestion.json_loader import load_json
from src.matching.matcher import Matcher
from src.utils.config import SUPABASE_URL, SUPABASE_KEY 
import uuid

app = FastAPI(title="OCL Mapper API")

# Supabase Setup
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load dictionary
json_file_path = "data/raw/export.json"
concepts_data = load_json(json_file_path)

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
matcher = Matcher(candidate_texts, candidate_ids)

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
        # Fetch feedback from Supabase
        corrected_matches = (
            supabase.from_("feedback_store")
            .select("*")
            .eq("term", term)
            .execute()
        )
        
        print(f"Retrieved Feedback for '{term}': {corrected_matches.data}")  # Debugging Output

        # If feedback exists, override results and show only the corrected match
        if corrected_matches.data:
            feedback_result = [
                {
                    "candidate_id": correct["candidate_id"],
                    "candidate_text": correct["candidate_text"],
                    "similarity_score": 1.0,  # Force confidence to max
                    "adjusted_by_feedback": True
                }
                for correct in corrected_matches.data
            ]
            results.append({"term": term, "matches": feedback_result})
        
        else:
            # Run normal matching if no feedback exists
            match_result = matcher.match(term, top_k=3)
            results.append({"term": term, "matches": match_result})

    return {"results": results}

@app.post("/feedback")
async def store_feedback(feedback: dict):
    """
    Stores user feedback in Supabase and injects the corrected match into the candidate list.
    """
    term = feedback.get("term")
    correct_match = feedback.get("correct_match")

    if not term or not correct_match:
        raise HTTPException(status_code=400, detail="Missing 'term' or 'correct_match' in feedback.")

    # Ensure data is stored correctly in Supabase
    data = {
        "id": str(uuid.uuid4()),  # Generate a unique ID
        "term": term,
        "candidate_id": correct_match["candidate_id"],
        "candidate_text": correct_match["candidate_text"]
    }
    
    # Insert into Supabase
    response = supabase.from_("feedback_store").insert(data).execute()
    
    # Debugging: Confirm the data was stored
    print(f" Feedback Stored: {response.data}")

    # Inject feedback term into the matcher dynamically
    if correct_match["candidate_text"] not in matcher.candidate_texts:
        matcher.candidate_texts.append(correct_match["candidate_text"])
        matcher.candidate_ids.append(correct_match["candidate_id"])
        new_embedding = matcher.embedder.get_embedding(correct_match["candidate_text"])
        matcher.candidate_embeddings = np.vstack([matcher.candidate_embeddings, new_embedding])

    return {"message": "Feedback stored and will be applied instantly."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
