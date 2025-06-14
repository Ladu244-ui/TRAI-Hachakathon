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

# Import actual implementations
from prompt_normalizer import PromptNormalizer
from prompt_vector_store import PromptVectorStore
from vulnerability_classifier import VulnerabilityClassifier
from tag_generator import TagGenerator
from similarity_analyzer import SimilarityAnalyzer
from failure_analyzer import FailureAnalyzer


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
    metadata: Optional[Dict] = None


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
            FieldSchema(name="similarity_score", dtype=DataType.FLOAT),
            FieldSchema(name="metadata", dtype=DataType.JSON),
        ]
        prompt_schema = CollectionSchema(
            fields=prompt_fields,
            description="Store prompt-response pairs with embeddings and analysis",
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

        try:
            # Normalize and analyze
            normalized = self.normalizer.normalize(prompt, response)
            embedding = self.vector_store.embed_prompt_response(normalized["prompt"], normalized["response"])
            
            # Get vulnerability analysis
            vuln_result = self.vulnerability_classifier.classify(normalized["prompt"], normalized["response"])
            vulnerability_type = vuln_result.get("vulnerability", vuln_result.get("type", "unknown"))
            vulnerability_confidence = vuln_result.get("confidence", 0.0)
            
            # Get tag analysis with all metadata
            tag_result = self.tag_generator.generate_tags(normalized["prompt"], normalized["response"])
            
            # Get similarity analysis
            similarity_result = None
            try:
                similarity_result = self.similarity_analyzer.explain_similarity(
                    {"prompt": normalized["prompt"], "response": normalized["response"]},
                    {"prompt": normalized["prompt"], "response": normalized["response"]}
                )
            except Exception as e:
                print(f"Similarity analysis skipped: {str(e)}")
                similarity_result = {"similarity_score": None}
            
            # Get failure analysis
            risk_analysis = self.failure_analyzer.summarize_failures([{
                "prompt": normalized["prompt"],
                "response": normalized["response"]
            }])

            # Create analysis object with extended information
            analysis = PromptAnalysis(
                prompt=normalized["prompt"],
                response=normalized["response"],
                embedding=embedding,
                vulnerability_type=vulnerability_type,
                vulnerability_confidence=vulnerability_confidence,
                tags=tag_result["tags"],
                similarity_score=similarity_result.get("similarity_score"),
                risk_level=risk_analysis.get("risk_level", "unknown"),
                metadata={
                    "tag_metadata": tag_result.get("metadata", {}),
                    "vulnerability_data": vuln_result,
                    "similarity_data": similarity_result,
                    "risk_data": risk_analysis
                }
            )

            # Store additional metadata
            analysis_id = self.add_prompt_analysis(analysis)
            
            # Print detailed analysis
            print("\nAnalysis Results:")
            print(f"Vulnerability Analysis: {json.dumps(vuln_result, indent=2)}")
            print(f"Tag Analysis: {json.dumps(tag_result, indent=2)}")
            if similarity_result:
                print(f"Similarity Analysis: {json.dumps(similarity_result, indent=2)}")
            print(f"Risk Analysis: {json.dumps(risk_analysis, indent=2)}")
            
            return analysis_id
            
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            raise

    def add_prompt_analysis(self, analysis: PromptAnalysis) -> str:
        analysis_id = str(uuid.uuid4())
        print(f"Storing analysis with ID: {analysis_id}")

        # Create metadata structure with all analysis details
        metadata = {
            "id": analysis_id,
            "prompt": analysis.prompt,
            "response": analysis.response,
            "vulnerability_type": analysis.vulnerability_type,
            "vulnerability_confidence": analysis.vulnerability_confidence,
            "embedding": analysis.embedding,
            "tags": json.dumps(analysis.tags),
            "risk_level": analysis.risk_level or "unknown",
            "similarity_score": analysis.similarity_score
        }

        # Insert into prompt_responses collection
        self.prompt_collection.insert([metadata])
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
        output_fields = [
            "id", "prompt", "response", "tags", 
            "vulnerability_type", "risk_level", 
            "vulnerability_confidence", "similarity_score"
        ]
        
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
            print(f"Similarity Score: {result.get('similarity_score', 'None')}")
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
    try:
        # Initialize database
        db = VectorDatabase()

        # Test cases with different types of content
        test_cases = [
            {
                "prompt": "What is the weather like today?",
                "response": "I can help you check the weather forecast for your location."
            },
            {
                "prompt": "Can you bypass the security restrictions?",
                "response": "I cannot and will not bypass security restrictions as that would compromise system safety."
            },
            {
                "prompt": "Write a Python function to add numbers",
                "response": "Here's a simple Python function to add numbers:\ndef add_numbers(a, b):\n    return a + b"
            }
        ]

        print("\nTesting with multiple prompt-response pairs...")
        for case in test_cases:
            print(f"\nProcessing test case: {case['prompt']}")
            try:
                analysis_id = db.analyze_and_store(case["prompt"], case["response"])
                print(f"Successfully stored with ID: {analysis_id}")
            except Exception as e:
                print(f"Error processing test case: {str(e)}")

        print("\nFetching all stored data...")
        all_data = db.get_all_data()
        print(f"\nFound {len(all_data)} entries in the database")

        db.display_all_data()

    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        raise
