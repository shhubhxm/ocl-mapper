import numpy as np
import json
import os
from sklearn.metrics.pairwise import cosine_similarity
from src.model.embedder import BioBERTEmbedder
from src.ingestion.json_loader import load_json

feedback_file = "data/processed/feedback_store.json"

def load_feedback():
    """ Reloads feedback from file every time to ensure the latest corrections are used. """
    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

class Matcher:
    def __init__(self, candidate_texts, candidate_ids, embedder=None):
        self.embedder = embedder or BioBERTEmbedder()
        self.candidate_texts = candidate_texts
        self.candidate_ids = candidate_ids
        self.candidate_embeddings = np.array([self.embedder.get_embedding(text) for text in candidate_texts])

    def match(self, query_text, top_k=5):
        """ Perform matching and dynamically adjust based on feedback. """
        feedback_store = load_feedback()  # ✅ Always reload latest feedback

        query_embedding = self.embedder.get_embedding(query_text)
        similarities = cosine_similarity([query_embedding], self.candidate_embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            match = {
                "candidate_id": self.candidate_ids[idx],
                "candidate_text": self.candidate_texts[idx],
                "similarity_score": float(similarities[idx])
            }

            # ✅ If feedback exists, increase similarity score for correct matches
            if query_text in feedback_store:
                for correct_match in feedback_store[query_text]:
                    if match["candidate_text"] == correct_match["candidate_text"]:
                        match["similarity_score"] += 0.05  # Boost user-approved matches

            results.append(match)

        return results
