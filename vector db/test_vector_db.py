import asyncio
import sys
import os

# Add necessary paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
guardrail_backend = os.path.join(parent_dir, 'guardrail_sentinel_backend')

# Add all necessary directories to Python path
sys.path.extend([
    current_dir,
    parent_dir,
    guardrail_backend,
    os.path.join(guardrail_backend, 'utils'),
    os.path.join(guardrail_backend, 'services')
])

from vector_database import VectorDatabase
from prompt_generator import generate_injection_prompts
from prompt_tester import test_single_prompt

async def test_vector_db_with_dynamic_prompts():
    try:
        # Initialize database
        db = VectorDatabase()

        # Generate prompts for different business types
        business_types = ["healthcare", "banking", "education", "e-commerce", "insurance"]
        
        print("\nTesting with dynamically generated prompts...")
        
        for business_type in business_types:
            # Generate prompts for this business type
            prompts = await generate_injection_prompts(business_type, count=1)
            
            for prompt in prompts:
                # Test the prompt against a demo endpoint (replace with your actual endpoint)
                test_endpoint = "https://web-production-8e40c.up.railway.app/chat/"  # Replace with your endpoint
                result = await test_single_prompt(test_endpoint, prompt)
                
                print(f"\nProcessing test case for {business_type}:")
                print(f"Prompt: {result.prompt}")
                print(f"Response: {result.response}")
                
                try:
                    analysis_id = db.analyze_and_store(result.prompt, result.response)
                    print(f"Successfully stored with ID: {analysis_id}")
                except Exception as e:
                    print(f"Error processing test case: {str(e)}")

        print("\nFetching all stored data...")
        db.display_all_data()

    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_vector_db_with_dynamic_prompts())
