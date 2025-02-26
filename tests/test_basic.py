# tests/test_basic.py
import unittest
from src.ingestion.csv_loader import load_csv
from src.model.embedder import BioBERTEmbedder
from src.matching.matcher import Matcher

class TestOCLMapper(unittest.TestCase):
    def test_csv_loader(self):
        # For testing purposes, you might create a small CSV in the tests folder.
        # Here we assume a file 'tests/sample.csv' exists.
        try:
            df = load_csv("data/processed/datatest_MSF_MentalHealth.csv")
            self.assertIn("Label", df.columns)
        except Exception as e:
            self.fail(f"CSV loader raised an exception: {e}")

    def test_embedder(self):
        embedder = BioBERTEmbedder()
        embedding = embedder.get_embedding("Test phrase")
        self.assertIsNotNone(embedding)
        self.assertEqual(len(embedding.shape), 1)  # Expecting a 1D embedding vector

    def test_matcher(self):
        candidate_texts = ["Acute myocardial infarction", "Chronic heart failure", "Hypertension"]
        candidate_ids = [101, 102, 103]
        matcher = Matcher(candidate_texts, candidate_ids)
        results = matcher.match("Heart attack", top_k=2)
        self.assertEqual(len(results), 2)
        self.assertTrue(all("similarity_score" in r for r in results))

if __name__ == '__main__':
    unittest.main()
