# src/matching/matcher.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.model.embedder import BioBERTEmbedder
from src.ingestion.json_loader import load_json

def build_candidates_from_dict(concepts_data):
    """
    Extracts candidate terms from the dictionary concepts.
    """
    candidate_texts = []
    candidate_ids = []
    
    for concept in concepts_data:
        # Use "display_name" as the primary term
        if "display_name" in concept:
            candidate_texts.append(concept["display_name"].lower().strip())
            candidate_ids.append(concept["uuid"])
        
        # Also add synonyms/alternative names
        if "names" in concept:
            for name_entry in concept["names"]:
                if "name" in name_entry:
                    candidate_texts.append(name_entry["name"].lower().strip())
                    candidate_ids.append(concept["uuid"])  # Same UUID as primary term

    return candidate_texts, candidate_ids

class Matcher:
    def __init__(self, candidate_texts, candidate_ids, embedder=None):
        self.embedder = embedder or BioBERTEmbedder()
        self.candidate_texts = candidate_texts
        self.candidate_ids = candidate_ids
        self.candidate_embeddings = np.array([self.embedder.get_embedding(text) for text in candidate_texts])

    def match(self, query_text, top_k=5):
        query_embedding = self.embedder.get_embedding(query_text)
        similarities = cosine_similarity([query_embedding], self.candidate_embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = []
        for idx in top_indices:
            result = {
                "candidate_id": self.candidate_ids[idx],
                "candidate_text": self.candidate_texts[idx],
                "similarity_score": float(similarities[idx])
            }
            results.append(result)
        return results

if __name__ == "__main__":
    # Load real dictionary data
    concepts_data = load_json("data/raw/export.json")

    # Build candidate lists from the dictionary
    candidate_texts, candidate_ids = build_candidates_from_dict(concepts_data)

    # Initialize matcher with real dictionary data
    matcher = Matcher(candidate_texts, candidate_ids)

    # Test matching function with a sample query
    test_query = "Musculoskeletal pain"
    match_results = matcher.match(test_query, top_k=3)

    print(f"\n🔍 Matching Results for '{test_query}':")
    for i, result in enumerate(match_results, start=1):
        print(f"{i}. {result['candidate_text']} (ID: {result['candidate_id']}, Score: {result['similarity_score']:.2f})")
