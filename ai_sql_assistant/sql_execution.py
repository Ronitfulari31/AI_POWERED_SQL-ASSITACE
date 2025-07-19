import pandas as pd
import psycopg2
from app_secrets import PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD
from error_handler import ErrorHandler

def execute_query(sql, schema):
    connection_params = {
        'host': PG_HOST,
        'port': PG_PORT,
        'database': PG_DATABASE,
        'user': PG_USER,
        'password': PG_PASSWORD
    }

    try:
        conn = psycopg2.connect(**connection_params)
        cur = conn.cursor()

        if schema:
            cur.execute(f"SET search_path TO {schema}")
        
        cur.execute(sql)
        
        if sql.lower().strip().startswith(('select', 'with')):
            results = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            return pd.DataFrame(results, columns=column_names)
        else:
            conn.commit()
            return pd.DataFrame([{'message': 'Query executed successfully'}])

    except Exception as e:
        ErrorHandler.handle_and_display(e)
        return pd.DataFrame([{'error': str(e)}])

    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass
