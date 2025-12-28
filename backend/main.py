import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from db.helpers import get_postgres_schema, execute_sql, get_query_plan
from services.llm import generate_sql_prompt, set_schema, explain_sql, explain_plan, warm_up_ollama, \
    contains_known_table

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Load database credentials from environment variables
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "ai2query")
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pass")


class DBConnection(BaseModel):
    host: Optional[str] = Field(default=DB_HOST)
    port: Optional[int] = Field(default=DB_PORT)
    dbname: Optional[str] = Field(default=DB_NAME)
    user: Optional[str] = Field(default=DB_USER)
    password: Optional[str] = Field(default=DB_PASSWORD)


@app.post("/connect")
def connect(creds: DBConnection = DBConnection()):
    try:
        schema = get_postgres_schema(creds)
        set_schema(schema)
        app.state.db_creds = creds
        warm_up_ollama()
        logger.info("Database schema loaded and connection stored.")
        return {"status": "connected", "schema_loaded": True}
    except Exception as e:
        logger.error(f"DB connection failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Connection failed")


class QuestionOnly(BaseModel):
    question: str


@app.post("/generate")
def generate(query: QuestionOnly):
    if not hasattr(app.state, "db_creds"):
        raise HTTPException(status_code=400, detail="Database not connected")

    creds = app.state.db_creds
    max_attempts = 3
    attempts = 0
    last_error = None
    sql = None
    result = []

    while attempts < max_attempts:
        sql = generate_sql_prompt(query.question, error=last_error)

        if not contains_known_table(sql):
            return {
                "sql": sql,
                "error": "No known table was referenced in the generated query.",
                "attempts": attempts + 1,
            }

        try:
            result = execute_sql(sql, creds)
            logger.info(f"SQL execution succeeded on attempt {attempts + 1}")
            break
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Attempt {attempts + 1} failed: {last_error}")
            attempts += 1

    if attempts == max_attempts:
        return {
            "sql": sql,
            "error": last_error,
            "attempts": attempts,
        }

    try:
        plan_json = get_query_plan(sql, creds)
        explanation = explain_sql(sql)
        plan_explanation = explain_plan(plan_json)
    except Exception as e:
        explanation = "Query explanation failed."
        plan_explanation = "Query plan explanation failed."
        logger.warning("Failed during post-query explanation step: " + str(e))

    return {
        "sql": sql,
        "preview": result[:10],
        "explanation": explanation,
        "plan": plan_explanation,
        "attempts": attempts,
    }


@app.get("/health/db")
def health_db():
    try:
        creds = app.state.db_creds
        result = execute_sql("SELECT 1;", creds)
        return {"ok": True, "db": result}
    except Exception as e:
        logger.error("Health check failed: " + str(e))
        return {"ok": False, "error": str(e)}
