PROMPT_DB: dict[str, dict] = {}

def save_result(prompt_id: str, result: dict):
    PROMPT_DB[prompt_id] = result

def fetch_result(prompt_id: str) -> dict | None:
    return PROMPT_DB.get(prompt_id)

def fetch_all_results() -> dict[str, dict]:
    return PROMPT_DB