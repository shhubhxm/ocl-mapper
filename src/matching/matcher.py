# src/matching/matcher.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.model.embedder import BioBERTEmbedder

class Matcher:
    def __init__(self, candidate_texts, candidate_ids, embedder=None):
        self.embedder = embedder or BioBERTEmbedder()
        self.candidate_ids = candidate_ids
        # Precompute embeddings for candidate texts
        self.candidate_embeddings = np.array([self.embedder.get_embedding(text) for text in candidate_texts])
        self.candidate_texts = candidate_texts

    def match(self, query_text, top_k=5):
        """
        Returns the top_k matching candidates for a given query text.
        """
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
    # Testing the matcher with dummy candidate data
    candidate_texts = ["Acute myocardial infarction", "Chronic heart failure", "Hypertension"]
    candidate_ids = [101, 102, 103]
    matcher = Matcher(candidate_texts, candidate_ids)
    results = matcher.match("Heart attack", top_k=2)
    print("Match Results:", results)
