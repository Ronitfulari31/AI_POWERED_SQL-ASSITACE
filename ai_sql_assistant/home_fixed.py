from app_secrets import HUGGINGFACE_API_TOKEN
import os
import streamlit as st
from sql_execution import execute_sf_query
from langchain.prompts import load_prompt
from pathlib import Path
from PIL import Image
from app_secrets import PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD, SF_USER, SF_PASSWORD, SF_ACCOUNT, SF_WAREHOUSE, SF_DATABASE, SF_SCHEMA, SF_ROLE
import psycopg2
import snowflake.connector
from sql_execution import execute_query

client = InferenceClient(token=HUGGINGFACE_API_TOKEN)

def write_to_training_file(file_path, prompt, sql):
    try:
        with open(file_path, 'a') as file:  # Changed 'w' to 'a' for append mode
            file.write(f"\nprompt: {prompt}")
            file.write(f"\nsql: {sql}")
            file.write("\nlabel: 1\n\n")
        return "success"
    except Exception as e:
        print(f"Error writing to file: {str(e)}")
        return f"Problem writing to file: {str(e)}"

#project root directory
current_dir = Path(__file__).resolve()
root_dir = current_dir.parent  # The parent directory of the current file

# Ensure directories exist
if not os.path.exists(f"{root_dir}/trainings"):
    os.makedirs(f"{root_dir}/trainings")
if not os.path.exists(f"{root_dir}/images"):
    os.makedirs(f"{root_dir}/images")

#frontend
st.set_page_config(
    page_title="Query Assistant",
    page_icon="🌄"
)
st.sidebar.success("Select a page above")

tab_titles=[
    "Results",
    "Query",
    "ER Diagram"
]

st.title("Your Project Assistant")

def get_schemas(database_type):
    if database_type == "Postgres":
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

def get_tables(database_type, schema):
    if database_type == "Postgres":
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
            cur.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'")
            tables = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            return tables
        except Exception as e:
            st.error(f"Error fetching tables: {e}")
            return []
    elif database_type == "Snowflake":
        try:
            conn = snowflake.connector.connect(
                user=SF_USER,
                password=SF_PASSWORD,
                account=SF_ACCOUNT,
                warehouse=SF_WAREHOUSE,
                database=SF_DATABASE,
                schema=SF_SCHEMA,
                role=SF_ROLE
            )
            cursor = conn.cursor()
            cursor.execute(f"SHOW TABLES IN SCHEMA {SF_DATABASE}.{schema}")
            tables = [row[1] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return tables
        except Exception as e:
            st.error(f"Error fetching tables: {e}")
            return []
    else:
        return []

database_type = st.selectbox("Select Database Type", ["Postgres", "Snowflake"])
schemas = get_schemas(database_type)
schema = st.selectbox("Select Schema", schemas)
tables = get_tables(database_type, schema)
table = st.selectbox("Select Table", tables)
prompt = st.text_input("enter your query")
tabs = st.tabs(tab_titles)
with tabs[2]:
        image = Image.open("{}/images/ERD.png".format(root_dir))
        st.image(image,caption="Entity Relationship")

prompt_template = load_prompt(f"{root_dir}/prompts/tpch_prompt.yaml")
final_prompt = prompt_template.format(input=prompt)

if prompt:
    # Use InferenceClient for chat completion
    response = client.chat_completion(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0.7,
        max_tokens=256
    )
    query_text = response.choices[0].message.content.strip()
    # More robust SQL cleaning
    query_text = query_text.split('```sql')[-1].split('```')[0].strip()
    if not query_text:
        query_text = response.choices[0].message.content.strip()
    if database_type == "Postgres":
        output = execute_query(query_text, schema, table)
    elif database_type == "Snowflake":
        output = execute_sf_query(query_text, schema, table, database_type)
    with tabs[0]:
        st.write(output)
    with tabs[1]:
        st.write(query_text)
        add_to_training_data = st.button("Add to training data")
        if add_to_training_data:
             file_path="{}/trainings/gpt_trainings.txt".format(root_dir)
             write_to_file_status = write_to_training_file(file_path=file_path,prompt=prompt,sql=query_text)
             if write_to_file_status == "success":
                  st.write("Scenario added to trainings file")
             else:
                  st.write(write_to_file_status)
