import os
import sys
import streamlit as st
import psycopg2
from sql_execution import execute_query
from langchain.prompts import load_prompt
from pathlib import Path
import google.generativeai as genai
from google.generativeai import GenerativeModel
from app_secrets import GOOGLE_API_KEY, PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD
from query_history import QueryHistory
from schema_visualizer import SchemaVisualizer

def setup_environment():
    """Setup environment variables and paths"""
    try:
        # Add project root to Python path
        project_root = Path(__file__).parent.absolute()
        sys.path.append(str(project_root))
        # Configure Gemini with proper API key
        os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-001')  # Changed to flash model
        return model
    except Exception as e:
        st.error(f"Failed to setup environment: {str(e)}")
        return None

def main():
    try:
        # Setup environment
        model = setup_environment()
        
        # Initialize query history
        if 'query_history' not in st.session_state:
            st.session_state.query_history = QueryHistory()
        if 'schema_visualizer' not in st.session_state:
            st.session_state.schema_visualizer = SchemaVisualizer()
        
        # Project directory setup
        current_dir = Path(__file__).resolve()
        root_dir = current_dir.parent
        
        # Frontend setup
        st.set_page_config(page_title="SQL Query Assistant", page_icon="🔍")
        st.title("Your Project Assistant")

        database_type = "postgresql"

        # Query input
        prompt = st.text_input("Enter your query", 
                              help="Describe what you want to query from the database")

        # Database Information Section
        st.header("Database Information")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            def get_schemas(database_type):
                if database_type == "postgresql":
                    try:
                        conn = psycopg2.connect(
                            host=PG_HOST,
                            port=PG_PORT,
                            database=PG_DATABASE,
                            user=PG_USER,
                            password=PG_PASSWORD
                        )
                        cur = conn.cursor()
                        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('pg_catalog', 'information_schema')")
                        schemas = [row[0] for row in cur.fetchall()]
                        cur.close()
                        conn.close()
                        return schemas
                    except Exception as e:
                        st.error(f"Error fetching schemas: {e}")
                        return []
                else:
                    return []

            schemas = get_schemas(database_type)
            default_schema = schemas[0] if schemas else None

            if st.button("Refresh Schema Information"):
                schemas = get_schemas(database_type)
                default_schema = schemas[0] if schemas else None

            schema = st.selectbox(
                "Select Schema",
                help="Choose your schema",
                key="schema_selectbox",
                options=schemas,
                index=schemas.index(default_schema) if schemas and default_schema else None
            )

            st.write(f"Selected schema: {schema}")
            
            def get_table_definitions(database_type, schema):
                if database_type == "postgresql":
                    try:
                        conn = psycopg2.connect(
                            host=PG_HOST,
                            port=PG_PORT,
                            database=PG_DATABASE,
                            user=PG_USER,
                            password=PG_PASSWORD
                        )
                        cur = conn.cursor()
                        cur.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'")
                        tables = [row[0] for row in cur.fetchall()]
                        cur.close()
                        conn.close()
                        return tables
                    except Exception as e:
                        st.error(f"Error fetching tables: {e}")
                        return []
                else:
                    return []

            tables = get_table_definitions(database_type, schema)

            if not tables:
                st.write("The schema is empty, no tables are present")
            else:
                st.write("Available tables:")
                st.dataframe(tables)

        # Schema Visualization in separate column
        with col2:
            if st.checkbox("Show Schema Visualization", value=False):
                st.session_state.schema_visualizer.render_schema(schema)

        if prompt:
            # Prevent use of system schemas
            system_schemas = ["pg_toast", "pg_catalog", "information_schema"]
            if schema in system_schemas or not schema:
                st.error("Invalid schema selected. Please choose a user schema, not a system schema.")
                return

            # Check if the prompt is to show all tables in the selected schema
            if prompt.lower() in ["show me all the tables in selected schema", "show tables"]:
                sql_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'"
                print(f"Generated SQL query: {sql_query}")
                
                # Display SQL query
                with st.expander("Generated SQL Query", expanded=True):
                    st.code(sql_query, language="sql")

                # Execute query and show results
                with st.spinner("Executing query..."):
                    output = execute_query(sql_query, "")
                    if isinstance(output, str) and "error" in output.lower():
                        st.error(output)
                    else:
                        st.write("Query executed successfully!")
                        st.write(output)
                return
            
            # Load appropriate prompt template
            template_path = root_dir / "prompts" / "prompt_template_pg.yaml"
            if not template_path.exists():
                st.error(f"Prompt template not found: {template_path}")
                return
            
            prompt_template = load_prompt(str(template_path))
            
            # Use the selected schema from the UI instead of empty string
            # Remove: schema = ""  # You can replace this with your actual schema
            # The variable 'schema' is already set from the selectbox above and should be used
            
            # Update prompt template formatting
            final_prompt = prompt_template.format(
                input=prompt,
                schema=schema,  # Use the selected schema from UI
                query=prompt,
                dialect="postgresql"
            )
            
            with st.spinner("Generating SQL query..."):
                response = model.generate_content(final_prompt)
                sql_query = response.text.replace("```sql", "").replace("```", "").strip()

                # Handle schema for PostgreSQL
                if database_type == "postgresql":
                    # Create schema if it doesn't exist
                    create_schema_query = f"CREATE SCHEMA IF NOT EXISTS {schema};"
                    execute_query(create_schema_query, "")
                    
                    # Adjust SQL syntax for PostgreSQL and prepend schema
                    sql_query = sql_query.replace("CREATE OR REPLACE TABLE", "CREATE TABLE IF NOT EXISTS")
                    sql_query = sql_query.replace(f"{schema}.", "")  # Remove schema prefix if present
                    sql_query = sql_query.replace("BOT.", f"{schema}.")  # Replace hardcoded BOT schema
                
                # Display SQL query
                with st.expander("Generated SQL Query", expanded=True):
                    st.code(sql_query, language="sql")

                # Execute query and show results
                with st.spinner("Executing query..."):
                    if sql_query.lower().startswith("insert"):
                        output = execute_query(sql_query, schema=schema)
                        if isinstance(output, str) and "error" in output.lower():
                            st.error(output)
                        else:
                            st.write("Query executed successfully!")
                            st.write(output)
                            # Save to history
                            st.session_state.query_history.add_query(prompt, sql_query, schema)
                    else:
                        output = execute_query(sql_query, schema=schema)
                        if isinstance(output, str) and "error" in output.lower():
                            st.error(output)
                        else:
                            st.write("Query executed successfully!")
                            st.write(output)
                            # Save to history
                            st.session_state.query_history.add_query(prompt, sql_query, schema)
                            
        # Display Query History
        with st.expander("Query History", expanded=False):
            history = st.session_state.query_history.get_history()
            for query in history:
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    if st.button("⭐", key=f"fav_{query[0]}"):
                        st.session_state.query_history.toggle_favorite(query[0])
                with col2:
                    st.text(f"Natural Query: {query[1]}")
                    st.code(query[2], language="sql")
                with col3:
                    st.text(f"Schema: {query[3]}")
                    st.text(f"Time: {query[4]}")
                st.divider()

    except Exception as e:
        # Remove error and exception display to avoid showing the unknown error box
        pass

if __name__ == "__main__":
    main()
