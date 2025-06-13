import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np

class PromptVectorStore:
    def __init__(self):
        # Initialize the model and tokenizer
        self.model_name = "sentence-transformers/all-mpnet-base-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def mean_pooling(self, model_output, attention_mask):
        # Mean pooling to get sentence embeddings
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def get_embedding(self, prompt_text, response_text):
        # Combine prompt and response with a separator
        combined_text = f"Prompt: {prompt_text}\nResponse: {response_text}"
        
        # Tokenize and prepare input
        encoded_input = self.tokenizer(combined_text, padding=True, truncation=True, max_length=512, return_tensors='pt')
        encoded_input = {k: v.to(self.device) for k, v in encoded_input.items()}

        # Generate embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)
            sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
            # Normalize embeddings
            sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)

        # Convert to numpy array and return as raw float array
        return sentence_embeddings.cpu().numpy()[0].tolist()

    def embed_prompt_response(self, prompt_text, response_text):
        """Main function to generate embeddings for a prompt-response pair"""
        return self.get_embedding(prompt_text, response_text)

# Example usage
if __name__ == "__main__":
    vector_store = PromptVectorStore()
    
    # Example prompt-response pair
    prompt = "What is the capital of France?"
    response = "The capital of France is Paris."
    
    # Get embedding
    embedding = vector_store.embed_prompt_response(prompt, response)
    print(f"Generated embedding dimension: {len(embedding)}")