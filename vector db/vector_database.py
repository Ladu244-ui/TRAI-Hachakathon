"""
Prompt Analysis and Vector Database System

This module provides functionality to analyze, store, and query prompt-response pairs
with their embeddings and metadata in a Zilliz Cloud vector database.
"""

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

# Import analysis components
from prompt_normalizer import PromptNormalizer
from prompt_vector_store import PromptVectorStore
from vulnerability_classifier import VulnerabilityClassifier
from tag_generator import TagGenerator
from similarity_analyzer import SimilarityAnalyzer
from failure_analyzer import FailureAnalyzer


@dataclass
class PromptAnalysis:
    """Data class representing the analysis of a prompt-response pair."""
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
    """Main class for managing prompt analysis and vector database operations."""
    
    def __init__(self, 
                 uri: str = "https://in03-32f4507697bcbb5.serverless.gcp-us-west1.cloud.zilliz.com", 
                 user: str = "db_32f4507697bcbb5", 
                 password: str = "Dn4]~2vvaU?3[h}^",
                 db_name: str = "Free-01"):
        """
        Initialize connection to Zilliz Cloud and analysis components.
        
        Args:
            uri: Zilliz cloud URI
            user: Username for authentication
            password: Password for authentication
            db_name: Database name
        """
        self._initialize_database_connection(uri, user, password, db_name)
        self._initialize_analysis_components()
        self._create_collections()

    def _initialize_database_connection(self, uri: str, user: str, password: str, db_name: str):
        """Establish connection to Zilliz Cloud."""
        print(f"Connecting to Zilliz Cloud at {uri}...")
        try:
            connections.connect(
                uri=uri,
                user=user,
                password=password,
                db_name=db_name,
                secure=True
            )
            print("Successfully connected to Zilliz Cloud.")
        except Exception as e:
            print(f"Failed to connect to Zilliz Cloud: {str(e)}")
            raise

    def _initialize_analysis_components(self):
        """Initialize all analysis components."""
        self.normalizer = PromptNormalizer()
        self.vector_store = PromptVectorStore()
        self.vulnerability_classifier = VulnerabilityClassifier()
        self.tag_generator = TagGenerator()
        self.similarity_analyzer = SimilarityAnalyzer()
        self.failure_analyzer = FailureAnalyzer()

    def _create_collections(self):
        """Create or load the required collections in the database."""
        print("Creating or loading collections...")
        self.prompt_collection = self._get_or_create_collection(
            "prompt_responses",
            self._create_prompt_schema()
        )
        print("Collections are ready.")

    def _create_prompt_schema(self) -> CollectionSchema:
        """Create the schema for the prompt responses collection."""
        prompt_fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
            FieldSchema(name="prompt", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="response", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="vulnerability_type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="vulnerability_confidence", dtype=DataType.FLOAT),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
            FieldSchema(name="tags", dtype=DataType.JSON),
            FieldSchema(name="risk_level", dtype=DataType.VARCHAR, max_length=20, nullable=True),
            FieldSchema(name="similarity_score", dtype=DataType.FLOAT, nullable=True),
            FieldSchema(name="metadata", dtype=DataType.JSON, nullable=True),
        ]
        
        return CollectionSchema(
            fields=prompt_fields,
            description="Store prompt-response pairs with embeddings and analysis",
            enable_dynamic_field=True
        )

    def _get_or_create_collection(self, name: str, schema: CollectionSchema) -> Collection:
        """Get or create a collection with the given name and schema."""
        if utility.has_collection(name):
            print(f"Dropping existing collection: {name}")
            utility.drop_collection(name)
            
        print(f"Creating new collection: {name}")
        collection = Collection(name, schema)
        self._create_collection_index(collection)
        collection.load()
        return collection

    def _create_collection_index(self, collection: Collection):
        """Create index for the collection."""
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        collection.create_index("embedding", index_params)

    def analyze_and_store(self, prompt: str, response: str) -> str:
        """
        Analyze and store a prompt-response pair.
        
        Args:
            prompt: The input prompt
            response: The generated response
            
        Returns:
            The analysis ID for the stored record
        """
        print("\nAnalyzing new prompt-response pair...")

        try:
            analysis = self._perform_analysis(prompt, response)
            analysis_id = self._store_analysis(analysis)
            self._print_analysis_results(analysis)
            return analysis_id
            
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            raise

    def _perform_analysis(self, prompt: str, response: str) -> PromptAnalysis:
        """Perform all analysis steps on a prompt-response pair."""
        normalized = self.normalizer.normalize(prompt, response)
        embedding = self.vector_store.embed_prompt_response(normalized["prompt"], normalized["response"])
        
        vuln_result = self.vulnerability_classifier.classify(normalized["prompt"], normalized["response"])
        tag_result = self.tag_generator.generate_tags(normalized["prompt"], normalized["response"])
        similarity_result = self._perform_similarity_analysis(normalized)
        risk_analysis = self.failure_analyzer.summarize_failures([{
            "prompt": normalized["prompt"],
            "response": normalized["response"]
        }])

        return PromptAnalysis(
            prompt=normalized["prompt"],
            response=normalized["response"],
            embedding=embedding,
            vulnerability_type=vuln_result.get("vulnerability", vuln_result.get("type", "unknown")),
            vulnerability_confidence=vuln_result.get("confidence", 0.0),
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

    def _perform_similarity_analysis(self, normalized_data: Dict) -> Dict:
        """Perform similarity analysis with error handling."""
        try:
            return self.similarity_analyzer.explain_similarity(
                {"prompt": normalized_data["prompt"], "response": normalized_data["response"]},
                {"prompt": normalized_data["prompt"], "response": normalized_data["response"]}
            )
        except Exception as e:
            print(f"Similarity analysis skipped: {str(e)}")
            return {"similarity_score": None}

    def _print_analysis_results(self, analysis: PromptAnalysis):
        """Print the results of the analysis."""
        print("\nAnalysis Results:")
        print(f"Vulnerability Analysis: {json.dumps(analysis.metadata['vulnerability_data'], indent=2)}")
        print(f"Tag Analysis: {json.dumps({'tags': analysis.tags, 'metadata': analysis.metadata['tag_metadata']}, indent=2)}")
        if analysis.similarity_score is not None:
            print(f"Similarity Analysis: {json.dumps(analysis.metadata['similarity_data'], indent=2)}")
        print(f"Risk Analysis: {json.dumps(analysis.metadata['risk_data'], indent=2)}")

    def _store_analysis(self, analysis: PromptAnalysis) -> str:
        """Store the analysis results in the database."""
        analysis_id = str(uuid.uuid4())
        print(f"Storing analysis with ID: {analysis_id}")
        
        metadata = {
            "id": analysis_id,
            "prompt": analysis.prompt,
            "response": analysis.response,
            "vulnerability_type": analysis.vulnerability_type,
            "vulnerability_confidence": float(analysis.vulnerability_confidence),
            "embedding": [float(x) for x in analysis.embedding],
            "tags": json.dumps(analysis.tags),
            "risk_level": analysis.risk_level if analysis.risk_level else None,
            "similarity_score": float(analysis.similarity_score) if analysis.similarity_score is not None else None,
            "metadata": analysis.metadata
        }

        try:
            self.prompt_collection.insert([metadata])
            print("Data stored successfully in prompt_responses collection.")
        except Exception as e:
            print(f"Error storing data: {str(e)}")
            print("Metadata structure:", json.dumps(metadata, cls=CustomJSONEncoder))

        return analysis_id

    # ... (rest of the methods remain the same with similar structural improvements)

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle special data types."""
    def default(self, obj):
        if hasattr(obj, 'dtype'):
            return float(obj)
        return super().default(obj)


def format_collection_data(data: Dict) -> Dict:
    """Format collection data to be JSON serializable."""
    formatted = {}
    for key, value in data.items():
        if isinstance(value, (list, tuple)) and len(value) > 10:
            formatted[key] = f"{value[:3]} ... {value[-3:]} (len: {len(value)})"
        else:
            formatted[key] = value
    return formatted


if __name__ == "__main__":
    try:
        db = VectorDatabase()

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
        db.display_all_data()

    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        raise