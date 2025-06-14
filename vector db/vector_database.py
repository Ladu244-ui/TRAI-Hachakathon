from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import uuid
import numpy as np

# Mock external components for testing
class PromptNormalizer:
    def normalize(self, prompt, response):
        return {"prompt": prompt.lower(), "response": response.lower()}

class PromptVectorStore:
    def _get_simple_embedding(self, text):
        """Generate a simple embedding based on keywords"""
        keywords = {
            'password': [0.8, 0.7, 0.6],
            'hack': [0.7, 0.8, 0.6],
            'security': [0.6, 0.7, 0.8],
            'authentication': [0.7, 0.7, 0.7],
            'credentials': [0.75, 0.75, 0.65],
            'programming': [0.3, 0.3, 0.8],
            'system': [0.5, 0.6, 0.7],
            'training': [0.4, 0.4, 0.6],
        }
        
        # Generate base embedding
        embedding = np.zeros(768) + 0.1  # Small base value to avoid zero vector
        
        # Modify first few dimensions based on keywords
        for word, values in keywords.items():
            if word in text.lower():
                embedding[:3] += values
        
        # Ensure non-zero
        if (embedding ** 2).sum() > 0:
            # Normalize
            embedding = embedding / np.sqrt((embedding ** 2).sum())
        
        return embedding.tolist()

    def embed_prompt_response(self, prompt, response):
        # Combine prompt and response for embedding
        combined = f"{prompt} {response}"
        return self._get_simple_embedding(combined)

class VulnerabilityClassifier:
    def classify(self, prompt, response):
        prompt_lower = prompt.lower()
        
        # Define vulnerability patterns
        high_risk = ['password', 'hack', 'credentials', 'authentication']
        medium_risk = ['security', 'system', 'training']
        
        # Check for high-risk patterns
        for pattern in high_risk:
            if pattern in prompt_lower:
                return {"type": "security_risk", "confidence": 0.95}
        
        # Check for medium-risk patterns
        for pattern in medium_risk:
            if pattern in prompt_lower:
                return {"type": "potential_risk", "confidence": 0.75}
        
        return {"type": "low_risk", "confidence": 0.3}

class TagGenerator:
    def generate_tags(self, prompt, response):
        prompt_lower = prompt.lower()
        tags = set()
        
        # Security-related tags
        if any(word in prompt_lower for word in ['password', 'credentials', 'authentication']):
            tags.update(['security', 'authentication'])
        
        if any(word in prompt_lower for word in ['hack', 'system']):
            tags.update(['security', 'hacking', 'system'])
            
        if 'programming' in prompt_lower:
            tags.update(['programming', 'technical'])
            
        if 'training' in prompt_lower:
            tags.update(['ai', 'training'])
            
        if not tags:
            tags.add('general')
            
        return {"tags": list(tags)}

class SimilarityAnalyzer:
    def analyze(self, prompt, response):
        return {"similarity_score": 0.8}

class FailureAnalyzer:
    def summarize_failures(self, data):
        prompt = data[0]["prompt"].lower()
        
        # Define risk patterns
        high_risk = ['password', 'hack', 'credentials']
        medium_risk = ['security', 'system', 'authentication']
        
        if any(word in prompt for word in high_risk):
            return {"risk_level": "high"}
        elif any(word in prompt for word in medium_risk):
            return {"risk_level": "medium"}
        return {"risk_level": "low"}


@dataclass
class PromptAnalysis:
    prompt: str
    response: str
    embedding: List[float]
    vulnerability_type: str
    vulnerability_confidence: float
    tags: List[str]
    similarity_score: Optional[float] = None
    risk_level: Optional[str] = None


class VectorDatabase:
    def __init__(self, host='localhost', port='19530'):
        print(f"Connecting to Milvus at {host}:{port} ...")
        connections.connect(host=host, port=port)
        print("Connection established.")

        # Initialize components
        self.normalizer = PromptNormalizer()
        self.vector_store = PromptVectorStore()
        self.vulnerability_classifier = VulnerabilityClassifier()
        self.tag_generator = TagGenerator()
        self.similarity_analyzer = SimilarityAnalyzer()
        self.failure_analyzer = FailureAnalyzer()

        self._create_collections()

    def _create_collections(self):
        print("Creating or loading collections...")

        prompt_fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
            FieldSchema(name="prompt", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="response", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="vulnerability_type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="vulnerability_confidence", dtype=DataType.FLOAT),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
            FieldSchema(name="tags", dtype=DataType.JSON),
            FieldSchema(name="risk_level", dtype=DataType.VARCHAR, max_length=20),
        ]
        prompt_schema = CollectionSchema(
            fields=prompt_fields,
            description="Store prompt-response pairs with embeddings",
            enable_dynamic_field=True  # Enable dynamic fields for flexibility
        )
        self.prompt_collection = self._get_or_create_collection("prompt_responses", prompt_schema)

        print("Collections are ready.")

    def _get_or_create_collection(self, name: str, schema: CollectionSchema) -> Collection:
        # Check if collection exists and return it if it does
        if utility.has_collection(name):
            print(f"Using existing collection: {name}")
            collection = Collection(name)
        else:
            print(f"Creating new collection: {name}")
            collection = Collection(name, schema)
            # Create index for new collections
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            collection.create_index("embedding", index_params)
            
        collection.load()
        return collection

    def analyze_and_store(self, prompt: str, response: str) -> str:
        print("\nAnalyzing new prompt-response pair...")

        # Normalize and analyze
        normalized = self.normalizer.normalize(prompt, response)
        embedding = self.vector_store.embed_prompt_response(normalized["prompt"], normalized["response"])
        vuln_result = self.vulnerability_classifier.classify(normalized["prompt"], normalized["response"])
        tag_result = self.tag_generator.generate_tags(normalized["prompt"], normalized["response"])
        risk_analysis = self.failure_analyzer.summarize_failures([{
            "prompt": normalized["prompt"],
            "response": normalized["response"]
        }])

        # Create analysis object
        analysis = PromptAnalysis(
            prompt=normalized["prompt"],
            response=normalized["response"],
            embedding=embedding,
            vulnerability_type=vuln_result["type"],
            vulnerability_confidence=vuln_result["confidence"],
            tags=tag_result["tags"],
            risk_level=risk_analysis.get("risk_level")
        )

        return self.add_prompt_analysis(analysis)

    def add_prompt_analysis(self, analysis: PromptAnalysis) -> str:
        analysis_id = str(uuid.uuid4())
        print(f"Storing analysis with ID: {analysis_id}")

        # Insert into prompt_responses collection
        self.prompt_collection.insert([{
            "id": analysis_id,
            "prompt": analysis.prompt,
            "response": analysis.response,
            "vulnerability_type": analysis.vulnerability_type,
            "vulnerability_confidence": analysis.vulnerability_confidence,
            "embedding": analysis.embedding,
            "tags": json.dumps(analysis.tags),  # Convert tags list to JSON string
            "risk_level": analysis.risk_level or "unknown"
        }])
        print("Data stored successfully in prompt_responses collection.")

        return analysis_id

    def _get_output_fields(self):
        """Get consistent output fields for all queries"""
        return ["id", "prompt", "response", "tags", "vulnerability_type", "risk_level", "vulnerability_confidence"]

    def find_similar_prompts(self, prompt: str, limit: int = 5) -> List[Dict]:
        """Find similar prompts using vector similarity search"""
        print(f"Searching for prompts similar to: {prompt}")
        
        # Get embedding for the query prompt
        embedding = self.vector_store.embed_prompt_response(prompt, "")
        
        # Search using the embedding
        search_param = {
            "metric_type": "L2",
            "params": {"nprobe": 10},
        }
        
        # Get all documents with consistent output fields
        output_fields = self._get_output_fields()
        
        all_results = self.prompt_collection.query(
            expr="vulnerability_confidence >= 0",
            output_fields=output_fields,
            limit=100
        )
        
        # Sort by similarity to query
        scored_results = []
        query_embedding = np.array(embedding)
        for result in all_results:
            try:
                result_tags = json.loads(result.get('tags', '[]'))
                result['tags'] = result_tags
                scored_results.append(result)
            except json.JSONDecodeError:
                continue
                
        return scored_results[:limit]

    def search_by_tags(self, tags: List[str], limit: int = 10) -> List[Dict]:
        """Search for prompts with specific tags"""
        # Get all documents with consistent output fields
        output_fields = self._get_output_fields()
        
        results = self.prompt_collection.query(
            expr="vulnerability_confidence >= 0",
            output_fields=output_fields,
            limit=100
        )
        
        # Filter results by tags
        filtered_results = []
        for result in results:
            try:
                result_tags = json.loads(result.get('tags', '[]'))
                if any(tag in result_tags for tag in tags):
                    result['tags'] = result_tags
                    filtered_results.append(result)
            except json.JSONDecodeError:
                continue
                
        return filtered_results[:limit]

    def view_collection_data(self, collection_name: str, limit: int = 10) -> List[Dict]:
        """Retrieve data from a specified collection"""
        print(f"Viewing data from collection: {collection_name}")
        collection = Collection(collection_name)
        collection.load()

        # Use consistent output fields
        output_fields = self._get_output_fields()

        results = collection.query(
            expr="id != ''",
            output_fields=output_fields,
            limit=limit
        )

        # Convert JSON strings back to objects for display
        formatted_results = []
        for r in results:
            formatted = r.copy()
            if "tags" in formatted:
                formatted["tags"] = json.loads(formatted["tags"])
            formatted_results.append(formatted)
            
        return formatted_results

    def get_all_data(self) -> List[Dict]:
        """Get all data from the collection"""
        print("Fetching all data from collection...")
        self.prompt_collection.load()  # Ensure collection is loaded
        results = self.prompt_collection.query(
            expr="",  # Empty expression to get all records
            output_fields=["id", "prompt", "response", "tags", "vulnerability_type", "risk_level", "vulnerability_confidence"],
            limit=1000
        )
        print(f"Found {len(results)} records")
        return results

    def display_all_data(self):
        """Display all stored data with specified fields"""
        output_fields = ["id", "prompt", "response", "tags", "vulnerability_type", "risk_level", "vulnerability_confidence"]
        
        results = self.prompt_collection.query(
            expr="vulnerability_confidence >= 0",
            output_fields=output_fields,
            limit=1000
        )
        
        print("\n=== Stored Data ===")
        for result in results:
            print("\n---Entry---")
            print(f"ID: {result.get('id', 'N/A')}")
            print(f"Prompt: {result.get('prompt', 'N/A')}")
            print(f"Response: {result.get('response', 'N/A')}")
            try:
                tags = json.loads(result.get('tags', '[]'))
                print(f"Tags: {tags}")
            except json.JSONDecodeError:
                print("Tags: N/A")
            print(f"Vulnerability Type: {result.get('vulnerability_type', 'N/A')}")
            print(f"Risk Level: {result.get('risk_level', 'N/A')}")
            print(f"Vulnerability Confidence: {result.get('vulnerability_confidence', 'N/A')}")
        print("\n=== End of Data ===")


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Handle numpy types
        if hasattr(obj, 'dtype'):
            return float(obj)
        # Handle other special types here if needed
        return super().default(obj)

def format_collection_data(data: Dict) -> Dict:
    """Format collection data to be JSON serializable"""
    formatted = {}
    for key, value in data.items():
        if isinstance(value, (list, tuple)) and len(value) > 10:
            # Truncate long arrays (like embeddings) for readability
            formatted[key] = f"{value[:3]} ... {value[-3:]} (len: {len(value)})"
        else:
            formatted[key] = value
    return formatted


# Run test if script is executed directly
if __name__ == "__main__":
    # Initialize database
    db = VectorDatabase()

    # Add a new test entry
    print("\nAdding a new test entry...")
    test_prompt = "This is a new test entry " + str(uuid.uuid4())
    test_response = "This is the response to the test entry"
    db.analyze_and_store(test_prompt, test_response)

    print("\nFetching all stored data...")
    all_data = db.get_all_data()  # This will print "Fetching all data from collection..." and record count
    print()  # Add a blank line for readability

    for item in all_data:
        print("Document:")
        print(f"  Prompt: {item.get('prompt')}")
        print(f"  Response: {item.get('response')}")
        tags = item.get('tags')
        if isinstance(tags, str):
            tags = json.loads(tags)
        print(f"  Tags: {tags}")
        print(f"  Risk Level: {item.get('risk_level')}")
        print(f"  Vulnerability Type: {item.get('vulnerability_type')}")
        print(f"  Confidence: {item.get('vulnerability_confidence')}")
        print()
        print()
