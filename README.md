# AI-SQL-Query-Generator_api

FastAPI backend service for QueryCraft AI — an intelligent SQL query generator and validator with strict read-only execution guardrails.

## Features
- **Natural Language to SQL**: Converts natural language prompts (e.g. "Show monthly sales by category") into executable, optimized SQL.
- **Strict Read-Only Safety Validation**: AST and token inspection to reject destructive operations (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`, etc.) and multi-statement injection attempts.
- **Deep Query Explanation**: Clause-by-clause breakdown (`SELECT`, `FROM & JOIN`, `WHERE`, `GROUP BY`, `ORDER BY`, `LIMIT`) plus business insights.
- **Embedded Database & Schema Inspector**: SQLite sample e-commerce database with auto-seeding.
- **Multi-Engine Support**: Built-in intelligent offline engine + Google Gemini API & OpenAI API integrations.

## Tech Stack
- Python 3.10+
- FastAPI & Uvicorn
- SQLParse & Pydantic
- SQLite (or PostgreSQL)

## Setup & Run

```bash
# 1. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Configure API keys
cp .env.example .env

# 4. Start the server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive API docs available at: `http://127.0.0.1:8000/docs`
