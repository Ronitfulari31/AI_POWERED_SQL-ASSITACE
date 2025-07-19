from typing import Optional
from dataclasses import dataclass

@dataclass
class QueryResponse:
    message: str
    sql_query: Optional[str] = None

def handle_natural_language_query(query: str) -> QueryResponse:
    query = query.lower().strip()
    
    # Common natural language patterns and their SQL translations
    translations = {
        "show me all": "SELECT * FROM",
        "show all": "SELECT * FROM",
        "list all": "SELECT * FROM",
        "display all": "SELECT * FROM",
        "get all": "SELECT * FROM"
    }
    
    # Convert natural language to SQL if possible
    for pattern, sql_prefix in translations.items():
        if query.startswith(pattern):
            table_name = query.replace(pattern, "").strip()
            if "customer" in table_name:
                return QueryResponse(
                    message="Executing query to show all customers",
                    sql_query="SELECT * FROM customer;"
                )
            elif table_name in ["orders", "suppliers", "products", "nations", "regions"]:
                return QueryResponse(
                    message=f"Executing query to show all {table_name}",
                    sql_query=f"SELECT * FROM {table_name};"
                )
    
    # Default response for unrecognized queries
    return QueryResponse(
        message="Please rephrase your query using SQL or specify what information you need.",
        sql_query=None
    )
