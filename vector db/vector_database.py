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
        self._create_collections()

    def _create_collections(self):
        print("Creating or loading collections...")

        prompt_fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
            FieldSchema(name="prompt", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="response", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="vulnerability_type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="vulnerability_confidence", dtype=DataType.FLOAT),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
        ]
        prompt_schema = CollectionSchema(fields=prompt_fields, description="Store prompt-response pairs with embeddings")
        self.prompt_collection = self._get_or_create_collection("prompt_responses", prompt_schema)

        vuln_fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
            FieldSchema(name="type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="confidence", dtype=DataType.FLOAT),
            FieldSchema(name="risk_level", dtype=DataType.VARCHAR, max_length=20),
            FieldSchema(name="data", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
        ]
        vuln_schema = CollectionSchema(fields=vuln_fields, description="Store vulnerability analysis results")
        self.vulnerability_collection = self._get_or_create_collection("vulnerabilities", vuln_schema)

        tag_fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
            FieldSchema(name="tags", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="vulnerability_type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="data", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)  # Adding vector field
        ]
        tag_schema = CollectionSchema(fields=tag_fields, description="Store generated tags and metadata")
        self.tag_collection = self._get_or_create_collection("tags", tag_schema)

        print("Collections are ready.")

    def _get_or_create_collection(self, name: str, schema: CollectionSchema) -> Collection:
        if utility.has_collection(name):
            print(f"Loading existing collection: {name}")
            collection = Collection(name)
            collection.load()
        else:
            print(f"Creating new collection: {name}")
            collection = Collection(name, schema)
            collection.create_index(field_name="embedding", index_params={"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 1024}})
            collection.load()
        return collection

    def add_prompt_analysis(self, analysis: PromptAnalysis) -> str:
        analysis_id = str(uuid.uuid4())
        print(f"Adding new PromptAnalysis with id: {analysis_id}")

        # Insert into prompt_responses collection
        self.prompt_collection.insert([{
            "id": analysis_id,
            "prompt": analysis.prompt,
            "response": analysis.response,
            "vulnerability_type": analysis.vulnerability_type,
            "vulnerability_confidence": analysis.vulnerability_confidence,
            "embedding": analysis.embedding
        }])
        print("Inserted data into 'prompt_responses' collection.")

        # Insert into vulnerabilities collection
        self.vulnerability_collection.insert([{
            "id": analysis_id,
            "type": analysis.vulnerability_type,
            "confidence": analysis.vulnerability_confidence,
            "risk_level": analysis.risk_level or "unknown",
            "data": json.dumps({
                "prompt": analysis.prompt,
                "response": analysis.response,
                "vulnerability_type": analysis.vulnerability_type
            }),
            "embedding": analysis.embedding
        }])
        print("Inserted data into 'vulnerabilities' collection.")

        # Insert tags with the same embedding as the prompt
        for tag in analysis.tags:
            self.tag_collection.insert([{
                "id": str(uuid.uuid4()),
                "tags": tag,
                "vulnerability_type": analysis.vulnerability_type,
                "data": json.dumps({
                    "prompt": analysis.prompt,
                    "response": analysis.response
                }),
                "embedding": analysis.embedding  # Using the same embedding as the prompt
            }])
        print("Inserted data into 'tags' collection.")

        print(f"Successfully added PromptAnalysis with id: {analysis_id}")
        return analysis_id

    def find_similar_prompts(self, embedding: List[float], n_results: int = 5) -> List[Dict]:
        print(f"Searching for top {n_results} similar prompts...")
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        self.prompt_collection.load()
        results = self.prompt_collection.search(
            data=[embedding],
            anns_field="embedding",
            param=search_params,
            limit=n_results,
            output_fields=["prompt", "response", "vulnerability_type", "vulnerability_confidence"]
        )
        self.prompt_collection.release()
        print(f"Search complete. Found {len(results[0])} results.")
        return [hit.entity._data for hit in results[0]]

    def get_vulnerability_statistics(self) -> Dict:
        print("Gathering vulnerability statistics...")
        self.vulnerability_collection.load()
        results = self.vulnerability_collection.query(
            expr="id != ''",
            output_fields=["type", "risk_level"]
        )
        self.vulnerability_collection.release()

        stats = {
            "total_entries": len(results),
            "vulnerability_types": {},
            "risk_levels": {}
        }

        for result in results:
            vuln_type = result['type']
            risk_level = result['risk_level']
            stats['vulnerability_types'][vuln_type] = stats['vulnerability_types'].get(vuln_type, 0) + 1
            stats['risk_levels'][risk_level] = stats['risk_levels'].get(risk_level, 0) + 1

        print(f"Stats collected: {stats}")
        return stats

    def search_by_tags(self, tags: List[str]) -> List[Dict]:
        print(f"Searching entries with tags: {tags}")
        tag_string = ",".join(tags)
        self.tag_collection.load()
        results = self.tag_collection.query(
            expr=f'tags like "%{tag_string}%"',
            output_fields=["id", "tags", "vulnerability_type", "data"],
            limit=10
        )
        self.tag_collection.release()

        print(f"Found {len(results)} entries with matching tags.")
        return [
            {**result, "data": json.loads(result["data"])}
            for result in results
        ]

    def delete_analysis(self, analysis_id: str):
        print(f"Deleting analysis with id: {analysis_id}")
        self.prompt_collection.delete(f'id == "{analysis_id}"')
        self.vulnerability_collection.delete(f'id == "{analysis_id}"')
        self.tag_collection.delete(f'id == "{analysis_id}"')
        print("Deletion completed.")

if __name__ == "__main__":
    # Test the VectorDatabase class
    print("Testing VectorDatabase initialization...")
    db = VectorDatabase()
    print("VectorDatabase initialized successfully!")
    
    # Test data
    test_analysis = PromptAnalysis(
        prompt="What is your password?",
        response="I cannot provide passwords.",
        embedding=[0.1] * 768,  # Simple test embedding
        vulnerability_type="prompt_injection",
        vulnerability_confidence=0.95,
        tags=["security", "credentials", "sensitive"],
        risk_level="high"
    )
    
    # Add test analysis
    print("\nTesting data insertion...")
    analysis_id = db.add_prompt_analysis(test_analysis)
    print("Test completed successfully!")

