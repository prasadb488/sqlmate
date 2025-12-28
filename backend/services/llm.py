import json
import os
import logging
from typing import List, Dict
from ollama import Client

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "ollama")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "sqlcoder:7b-q4_0")

client = Client(host=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}")
schema_context: str = ""


def set_schema(schema: str):
    global schema_context
    schema_context = schema.strip()


def ask_ollama(messages: List[Dict[str, str]], model: str = None) -> str:
    model = model or OLLAMA_MODEL
    try:
        logger.info(f"Sending request to Ollama model: {model}")
        response = client.chat(model=model, messages=messages)
        return response["message"]["content"]
    except Exception as e:
        logger.error(f"Ollama call failed: {e}")
        raise


def generate_sql_prompt(question: str, error: str = None) -> str:
    if not schema_context:
        raise ValueError("Schema context is not set.")

    # Core system instructions
    system_msg = f"""You are a PostgreSQL expert. Generate an PostgreSQL query.
    You will only use the schema provided below.
    - Do NOT hallucinate tables or columns.
    - Use CTEs or subqueries where appropriate.
    - If the question is unanswerable, return a syntactically correct SELECT query that returns an empty result.
    
    Schema:
    {schema_context}
    """

    # Dynamic user prompt
    if error:
        user_msg = f"""The previous query failed with the error:
        {error}
        
        Please correct the SQL for the question, if the errors are missing table or columns, If the schema doesn't contain any table relevant to this question, return:
SELECT 'No matching table found' WHERE false;:
        {question}"""
    else:
        user_msg = f"""Generate a SQL query to answer:
        {question}"""

    # Send to LLM
    return ask_ollama([
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ])


def explain_sql(sql: str) -> str:
    return ask_ollama([{"role": "user", "content": f"Explain this SQL step-by-step:\n\n{sql}"}])


def explain_plan(plan_json: dict) -> str:
    plan_text = json.dumps(plan_json, indent=2)
    return ask_ollama([{"role": "user", "content": f"Explain this PostgreSQL query plan:\n\n{plan_text}"}])


def warm_up_ollama(model: str = "sqlcoder:7b-q4_0"):
    import time
    try:
        logger.info(f"Pulling and warming up model: {model}")
        client.pull(model=model)
        time.sleep(3)  # wait for Ollama to stabilize
        _ = client.generate(model=model, prompt="SELECT 1;")
        logger.info("Ollama model is ready.")
    except Exception as e:
        logger.error(f"Failed to warm up Ollama: {e}")


import re


def extract_table_names(schema: str) -> set:
    return set(re.findall(r'CREATE TABLE (\w+)', schema, re.IGNORECASE))


TABLE_NAMES = extract_table_names(schema_context)


def contains_known_table(sql: str) -> bool:
    for table in TABLE_NAMES:
        if re.search(rf'\b{re.escape(table)}\b', sql, re.IGNORECASE):
            return True
    return False