import json
from pathlib import Path
from typing import List

from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

from backend.db.helpers import execute_sql
from backend.services.llm import generate_sql_prompt
from frontend.app import creds


def bleu_score(reference_sql: str, generated_sql: str) -> float:
    reference_tokens = reference_sql.split()
    candidate_tokens = generated_sql.split()
    smoothie = SmoothingFunction().method4
    return sentence_bleu([reference_tokens], candidate_tokens, smoothing_function=smoothie)


def execution_match(ref_result: list, gen_result: list) -> bool:
    return ref_result == gen_result


def run_evaluation(creds):
    with open("tests/test_cases.json") as f:
        test_cases = json.load(f)

    results = []

    for case in test_cases:
        generated = generate_sql_prompt(case["question"])
        try:
            ref_result = execute_sql(case["sql"], creds)
            gen_result = execute_sql(generated, creds)
            exec_ok = execution_match(ref_result, gen_result)
        except Exception:
            exec_ok = False
            gen_result = []

        results.append({
            "question": case["question"],
            "reference_sql": case["sql"],
            "generated_sql": generated,
            "bleu": bleu_score(case["sql"], generated),
            "execution_match": exec_ok
        })

    with open("logs/eval_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def log_reflexion(data: dict):
    log_file = Path("logs/reflexion_logs.json")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    if log_file.exists():
        existing = json.loads(log_file.read_text())
    else:
        existing = []
    existing.append(data)
    log_file.write_text(json.dumps(existing, indent=2))


def retry_with_reflexion(question: str, max_attempts=3) -> (str, int, List[str]):
    error = None
    errors = []
    for attempt in range(max_attempts):
        sql = generate_sql_prompt(question, error)
        try:
            execute_sql(sql, creds)
            return sql, attempt + 1, errors
        except Exception as e:
            error = str(e)
            errors.append(error)
    return sql, max_attempts, errors
