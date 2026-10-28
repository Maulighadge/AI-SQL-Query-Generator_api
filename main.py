import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

from database import init_db, get_schema_details, get_schema_summary, execute_readonly_query
from validator import validate_readonly_sql
from llm_service import generate_sql_and_explanation, explain_sql_query

load_dotenv()

app = FastAPI(
    title="QueryCraft AI - SQL Generator & Explainer API",
    description="Natural language to safe SQL generator with database schema inspection and read-only execution.",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to ensure database is created and seeded
@app.on_event("startup")
def on_startup():
    init_db()

# Request Models
class GenerateRequest(BaseModel):
    prompt: str
    api_key: Optional[str] = None
    provider: Optional[str] = "auto"

class ExplainRequest(BaseModel):
    sql: str
    api_key: Optional[str] = None

class ValidateRequest(BaseModel):
    sql: str

class ExecuteRequest(BaseModel):
    sql: str
    max_rows: Optional[int] = 500

@app.get("/api/health")
def health_check():
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "healthy",
        "service": "AI SQL Query Generator Backend",
        "llm_providers": {
            "gemini_env_configured": has_gemini,
            "openai_env_configured": has_openai,
            "builtin_engine": True
        }
    }

@app.get("/api/schema")
def get_schema():
    """Returns database schema metadata and sample data for frontend exploration."""
    try:
        schema = get_schema_details()
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch schema: {str(e)}")

@app.get("/api/sample-queries")
def get_sample_queries():
    """Curated natural language starter prompts."""
    return [
        {
            "id": "monthly-sales-category",
            "title": "Monthly Sales by Category",
            "prompt": "Show monthly sales by category",
            "category": "Sales Trends",
            "description": "Calculates monthly revenue and volume per product line."
        },
        {
            "id": "top-products-revenue",
            "title": "Top 5 Products by Revenue",
            "prompt": "Show top 5 best-selling products by gross revenue",
            "category": "Products",
            "description": "Identifies top revenue generating merchandise."
        },
        {
            "id": "top-customers-spending",
            "title": "VIP Customers by Spend",
            "prompt": "Show top customers by total spending and order count",
            "category": "Customers",
            "description": "Highlights high lifetime-value customers."
        },
        {
            "id": "low-stock-alert",
            "title": "Low Stock Inventory (< 50)",
            "prompt": "Which products have low stock quantities under 50?",
            "category": "Inventory",
            "description": "Surfaces items at risk of stockouts."
        },
        {
            "id": "monthly-aov",
            "title": "Average Order Value (AOV)",
            "prompt": "Show average order value and total orders by month",
            "category": "Sales Trends",
            "description": "Monitors customer spending power trends over time."
        },
        {
            "id": "product-reviews-rating",
            "title": "Product Review Scores",
            "prompt": "Show average rating and total reviews for each product",
            "category": "Satisfaction",
            "description": "Analyzes customer feedback ratings."
        }
    ]

@app.post("/api/generate")
def generate_query(req: GenerateRequest):
    """
    Converts natural language question into SQL, validates read-only safety,
    and returns a structured explanation.
    """
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    schema_text = get_schema_summary()
    
    try:
        gen_result = generate_sql_and_explanation(
            prompt=req.prompt,
            schema_text=schema_text,
            api_key=req.api_key,
            provider=req.provider or "auto"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    sql = gen_result.get("sql", "").strip()
    
    # Perform strict safety validation
    validation = validate_readonly_sql(sql)

    return {
        "prompt": req.prompt,
        "sql": sql,
        "formatted_sql": validation.get("formatted_sql", sql),
        "validation": validation,
        "summary": gen_result.get("summary", ""),
        "clauses_breakdown": gen_result.get("clauses_breakdown", []),
        "business_value": gen_result.get("business_value", ""),
        "suggested_questions": gen_result.get("suggested_questions", []),
        "engine": gen_result.get("engine", "QueryCraft AI Engine")
    }

@app.post("/api/explain")
def explain_query(req: ExplainRequest):
    """Takes any SQL query and generates an in-depth clause-by-clause explanation."""
    if not req.sql or not req.sql.strip():
        raise HTTPException(status_code=400, detail="SQL query cannot be empty.")

    validation = validate_readonly_sql(req.sql)
    schema_text = get_schema_summary()
    
    try:
        explanation = explain_sql_query(
            sql=req.sql,
            schema_text=schema_text,
            api_key=req.api_key
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

    return {
        "sql": req.sql,
        "validation": validation,
        "explanation": explanation
    }

@app.post("/api/validate")
def validate_query(req: ValidateRequest):
    """Validates if a SQL query is read-only and free of destructive statements."""
    return validate_readonly_sql(req.sql)

@app.post("/api/execute")
def execute_query(req: ExecuteRequest):
    """
    Safely executes a read-only query and returns rows, columns, and timing metrics.
    Rejects any non-read-only queries.
    """
    # 1. Validation check
    val = validate_readonly_sql(req.sql)
    if not val["is_safe"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Security Violation: {val['reason']}"
        )

    # 2. Execution in read-only connection
    try:
        result = execute_readonly_query(req.sql, max_rows=req.max_rows or 500)
        return {
            "success": True,
            "data": result,
            "validation": val
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
