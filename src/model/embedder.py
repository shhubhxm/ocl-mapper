from transformers import AutoTokenizer, AutoModel
import torch

class BioBERTEmbedder:
    def __init__(self, model_name="dmis-lab/biobert-base-cased-v1.1"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()  # Set the model to evaluation mode

    def get_embedding(self, text):
        """
        Generates an embedding for the input text using the CLS token representation.
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            outputs = self.model(**inputs)
        # Return the CLS token embedding as a numpy array
        return outputs.last_hidden_state[:, 0, :].squeeze().numpy()

if __name__ == "__main__":
    embedder = BioBERTEmbedder()
    embedding = embedder.get_embedding("Acute myocardial infarction")
    print("Embedding shape:", embedding.shape)
    print(embedding)