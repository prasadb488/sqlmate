# SQLmate – AI-Powered SQL Query Assistant

**SQLmate** is an intelligent, containerized SQL assistant that converts natural language questions into executable SQL queries using local AI models. It provides detailed explanations of query logic, analyzes PostgreSQL execution plans, and automatically refines queries when errors occur. Built for secure, offline database analysis without cloud dependency.

---

## Core Features

### 1. Natural Language to SQL Conversion

- Transforms plain English questions into SQL queries using local LLMs via [Ollama](https://ollama.com).
- Automatically includes your database schema in prompts for context-aware query generation.
- Prevents hallucinated queries by validating referenced tables and columns.

### 2. Intelligent Query Explanation

- Describes the reasoning behind generated queries, including table selections and filtering logic.
- Executes `EXPLAIN (FORMAT JSON)` on working queries to analyze performance.
- Provides detailed breakdowns of execution plans and optimization opportunities.

### 3. Auto-Healing Error Recovery

- Detects SQL execution failures and captures error messages.
- Automatically retries up to 3 times, improving the query based on error feedback.
- Tracks all recovery attempts and documents successful resolutions.

### 4. Performance Evaluation

- Measures LLM effectiveness using:
  - Query execution validation
  - BLEU/ROUGE text similarity scores
  - Success rate across retry attempts
  - Quality scoring for explanations
- Includes test suite with sample natural language queries.

### 5. REST API Backend

- Simple HTTP endpoints for all functionality:
  - `/connect`: Set up database connection
  - `/generate`: Convert questions to SQL with explanations
  - `/logs/eval`: Review evaluation metrics
  - `/health/db`: Verify database status

### 6. Complete Docker Containerization

Fully containerized with Docker Compose for easy local deployment.

**Included Services:**

- `api`: FastAPI application server
- `ollama`: Local LLM provider (e.g., `sqlcoder:7b-q4_0`)
- `postgres`: PostgreSQL database
- `streamlit`: Web-based chat interface

---

## Tech Stack

| Layer       | Technology              |
| ----------- | ----------------------- |
| Frontend UI | Streamlit               |
| Backend API | FastAPI                 |
| LLM         | Ollama (`sqlcoder:7b`)  |
| Database    | PostgreSQL              |
| ORM         | SQLAlchemy              |
| Evaluation  | BLEU, Execution Match   |
| Deployment  | Docker & Docker Compose |

---

## API Endpoints

### `POST /connect`

Establishes a connection to PostgreSQL and loads the database schema.

```json
{
  "host": "localhost",
  "port": 5432,
  "dbname": "finance_db",
  "user": "postgres",
  "password": "postgres"
}
```

### `POST /generate`

Accepts a natural language question and returns a generated SQL query with explanation and performance analysis.

```json
{
  "question": "Show total revenue by customer."
}
```

Response example:

```json
{
  "sql": "...",
  "preview": [...],
  "explanation": "...",
  "plan": "...",
  "attempts": 1,
  "recovered": false
}
```

### `GET /health/db`

Verifies database connection status.

---

## Run Locally

### Prerequisites

- Docker

- Docker Compose

---

### 1. Clone the Repository

```bash
git clone https://github.com/prasadb488/sqlmate.git
cd sqlmate
```

### 2. Launch All Services

```bash
docker-compose up --build
```

This starts all components:

- `api`: FastAPI backend running on port 8000
- `ollama`: LLM service (sqlcoder or phi models)
- `postgres`: Database server with initial data
- `streamlit`: Interactive web interface on port 8501

---

## Example Queries

Try these natural language questions in the interface:

- `"What are the top 5 customers by revenue?"`
- `"Calculate average salary per department"`
- `"Which accounts have negative balances?"`

Sample test data and queries are in:  
`/tests/test_cases.json`

---

## Project Structure

```
sqlmate/
├── backend/
│   ├── db/
│   ├── services/
│   ├── evaluation/
│   └── main.py
├── frontend/
│   └── app.py
├── ollama/
│   └── Dockerfile
├── tests/
│   └── test_cases.json
├── docker-compose.yml
└── README.md
```

---

## License

MIT – Open for educational and commercial use.
