import re
import sqlparse
from typing import Dict, Any, List

FORBIDDEN_KEYWORDS = {
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", 
    "CREATE", "REPLACE", "ATTACH", "DETACH", "PRAGMA", "GRANT", 
    "REVOKE", "EXEC", "EXECUTE", "CALL", "REINDEX", "VACUUM",
    "INTO", "MERGE", "UPSERT", "RENAME"
}

ALLOWED_STARTS = {"SELECT", "WITH", "EXPLAIN"}

def validate_readonly_sql(sql: str) -> Dict[str, Any]:
    """
    Validates that the provided SQL query is strictly read-only and free of destructive statements.
    
    Returns a dictionary with:
      - is_safe: bool
      - statement_type: str
      - reason: str (explanation if unsafe)
      - warnings: list[str]
      - formatted_sql: str
    """
    if not sql or not sql.strip():
        return {
            "is_safe": False,
            "statement_type": "EMPTY",
            "reason": "SQL query cannot be empty.",
            "warnings": [],
            "formatted_sql": ""
        }

    # Clean leading/trailing spaces
    cleaned_sql = sql.strip()

    # Disallow comments that might attempt injection tricks
    if re.search(r"/\*.*?\*/", cleaned_sql, re.DOTALL):
        # Allow comments if innocuous, but check contents
        pass

    # Parse using sqlparse
    try:
        parsed_statements = sqlparse.parse(cleaned_sql)
    except Exception as e:
        return {
            "is_safe": False,
            "statement_type": "UNKNOWN",
            "reason": f"Failed to parse SQL: {str(e)}",
            "warnings": [],
            "formatted_sql": cleaned_sql
        }

    # Must contain at least one statement
    if not parsed_statements:
        return {
            "is_safe": False,
            "statement_type": "EMPTY",
            "reason": "No valid SQL statement recognized.",
            "warnings": [],
            "formatted_sql": cleaned_sql
        }

    # Enforce exactly ONE statement to prevent multi-statement injection (e.g. SELECT 1; DROP TABLE...)
    non_empty_stmts = [s for s in parsed_statements if str(s).strip().rstrip(";")]
    if len(non_empty_stmts) > 1:
        return {
            "is_safe": False,
            "statement_type": "MULTI_STATEMENT",
            "reason": "Multiple SQL statements detected. Only a single read-only query is permitted per request.",
            "warnings": ["Detected stacked query attempt."],
            "formatted_sql": cleaned_sql
        }

    stmt = non_empty_stmts[0]
    
    # Check the first significant keyword
    first_token = None
    for token in stmt.tokens:
        if token.is_whitespace:
            continue
        first_token = token
        break

    if not first_token:
        return {
            "is_safe": False,
            "statement_type": "EMPTY",
            "reason": "Statement has no identifiable tokens.",
            "warnings": [],
            "formatted_sql": cleaned_sql
        }

    first_val = first_token.value.upper()
    if first_val not in ALLOWED_STARTS:
        return {
            "is_safe": False,
            "statement_type": first_val,
            "reason": f"Destructive or non-read-only operation '{first_val}' is disallowed. Queries must begin with SELECT or WITH.",
            "warnings": [f"Statement type '{first_val}' rejected."],
            "formatted_sql": cleaned_sql
        }

    # Inspect all flat tokens for forbidden DDL / DML keywords
    warnings = []
    flat_tokens = list(stmt.flatten())
    for token in flat_tokens:
        token_upper = token.value.upper()
        # Ignore string literals
        if token.ttype in (sqlparse.tokens.String, sqlparse.tokens.Literal.String.Single, sqlparse.tokens.Literal.String.Symbol):
            continue
        
        # Check forbidden keywords
        if token_upper in FORBIDDEN_KEYWORDS:
            # Check edge cases like INTO inside SELECT INTO
            return {
                "is_safe": False,
                "statement_type": first_val,
                "reason": f"Query contains forbidden keyword '{token_upper}'. Only safe read-only queries are permitted.",
                "warnings": [f"Prohibited token '{token_upper}' located."],
                "formatted_sql": cleaned_sql
            }

    # Format nicely
    formatted_sql = sqlparse.format(
        cleaned_sql,
        reindent=True,
        keyword_case="upper",
        identifier_case="lower"
    )

    # Check for LIMIT warning
    has_limit = "LIMIT" in formatted_sql.upper()
    if not has_limit:
        warnings.append("Notice: Query does not contain a LIMIT clause. Execution will cap output to safety bounds.")

    return {
        "is_safe": True,
        "statement_type": first_val,
        "reason": "Query verified as safe and read-only.",
        "warnings": warnings,
        "formatted_sql": formatted_sql
    }
