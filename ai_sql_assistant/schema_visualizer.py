import streamlit as st
import psycopg2
from app_secrets import PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD

class SchemaVisualizer:
    def __init__(self):
        self.connection_params = {
            'host': PG_HOST,
            'port': PG_PORT,
            'database': PG_DATABASE,
            'user': PG_USER,
            'password': PG_PASSWORD
        }

    def get_table_info(self, schema_name):
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            # Get tables and their columns
            cur.execute("""
                SELECT 
                    t.table_name,
                    c.column_name,
                    c.data_type,
                    c.is_nullable
                FROM information_schema.tables t
                LEFT JOIN information_schema.columns c 
                    ON t.table_name = c.table_name AND t.table_schema = c.table_schema
                WHERE t.table_schema = %s
                ORDER BY t.table_name, c.ordinal_position
            """, (schema_name,))
            return cur.fetchall()
        except Exception as e:
            return []
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

    def render_schema(self, schema_name):
        table_info = self.get_table_info(schema_name)
        if not table_info:
            st.info("No tables found or unable to fetch schema information.")
            return
        current_table = None
        columns = []
        for row in table_info:
            table_name, column_name, data_type, is_nullable = row
            if table_name != current_table:
                if current_table is not None:
                    st.write(f"**{current_table}**")
                    st.write(", ".join(columns))
                current_table = table_name
                columns = []
            columns.append(f"{column_name} ({data_type}, {'NULL' if is_nullable == 'YES' else 'NOT NULL'})")
        if current_table is not None:
            st.write(f"**{current_table}**")
            st.write(", ".join(columns))