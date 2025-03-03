import numpy as np
import json
import os
from sklearn.metrics.pairwise import cosine_similarity
from supabase import create_client, Client
from src.model.embedder import BioBERTEmbedder
from src.utils.config import SUPABASE_URL, SUPABASE_KEY 

# Supabase Setup
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class Matcher:
    def __init__(self, candidate_texts, candidate_ids, embedder=None):
        self.embedder = embedder or BioBERTEmbedder()
        self.candidate_texts = candidate_texts
        self.candidate_ids = candidate_ids
        self.candidate_embeddings = np.array([self.embedder.get_embedding(text) for text in candidate_texts])

    def match(self, query_text, top_k=5):
        """ Perform matching and apply real-time feedback from Supabase. """
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

            # Fetch feedback for this query
            corrected_matches = (
                supabase.from_("feedback_store")
                .select("*")
                .eq("term", query_text)
                .execute()
            )

            # Apply feedback-based match boosting
            for correct in corrected_matches.data:
                if correct["candidate_text"] not in self.candidate_texts:
                    self.candidate_texts.append(correct["candidate_text"])
                    self.candidate_ids.append(correct["candidate_id"])
                    new_embedding = self.embedder.get_embedding(correct["candidate_text"])
                    self.candidate_embeddings = np.vstack([self.candidate_embeddings, new_embedding])

                if match["candidate_text"] == correct["candidate_text"]:
                    match["similarity_score"] = 1.0  # Force feedback match to top
                    match["adjusted_by_feedback"] = True

            results.append(match)

        # Ensure feedback match is always ranked first
        results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)

        return results
