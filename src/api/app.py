from fastapi import FastAPI, UploadFile, File, HTTPException
from src.ingestion.csv_loader import load_csv
from src.matching.matcher import Matcher

app = FastAPI(title="OCL Mapper API")

# Dummy candidate data; replace with full dictionary data as needed.
candidate_texts = ["Acute myocardial infarction", "Chronic heart failure", "Hypertension"]
candidate_ids = [101, 102, 103]
matcher = Matcher(candidate_texts, candidate_ids)

@app.post("/match")
async def match_terms(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open("temp.csv", "wb") as f:
            f.write(contents)
        df = load_csv("temp.csv")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV: {e}")

    results = []
    if "Label" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV missing 'Label' column")
    
    for term in df["Label"].dropna():
        match_result = matcher.match(term, top_k=3)
        results.append({"term": term, "matches": match_result})
    
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
