# SQL Query Assistant

This project is a Streamlit application that allows users to interact with Snowflake and PostgreSQL databases using natural language queries.

## Features

*   Connect to Snowflake and PostgreSQL databases.
*   Select a database and schema.
*   View available tables in the selected schema.
*   Enter natural language queries to generate SQL queries.
*   Execute SQL queries and view the results.

## File Structure

*   `ai_sql_assistant/`: Contains the main application code.
    *   `sql_assistant.py`: Main file that handles the UI and orchestrates the SQL query generation and execution.
    *   `sql_execution.py`: Contains the functions to connect to the database and execute SQL queries.
    *   `nlp_handler.py`: (Potentially) contains code for natural language processing to understand user input.
    *   `database/schema_viewer.py`: (Potentially) contains code to retrieve database schema information.
    *   `prompts/prompt_template.yaml`: Contains the prompt template used for generating SQL queries.
    *   `app_secrets.py`: Contains sensitive information like API keys and database credentials. **This file should be kept secure and not shared.**
    *   `home_fixed.py`: (Potentially) contains code for the home page of the application.
    *   `message_box.py`: (Potentially) contains code for displaying messages to the user.
    *   `Langchain_sf_con_sample.py`: (Potentially) contains a Langchain example for Snowflake connection.
    *   `insert_sample_data.py`: (Potentially) contains code to insert sample data into the database.
    *   `database/create_tables.py`: (Potentially) contains code to create tables in the database.
    *   `database/create_tables_pg.py`: (Potentially) contains code to create tables in PostgreSQL database.
    *   `trainings/gpt_trainings.txt`: (Potentially) contains training data for the GPT model.
*   `dbQuery.js`: (Potentially) contains JavaScript code for database queries.
*   `queryErrorHandler.js`: (Potentially) contains JavaScript code for handling query errors.
*   `list_models.py`: (Potentially) contains code for listing available models.
*   `requirements.txt`: Contains a list of Python packages required to run the application.

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    ```
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    ```bash
    # On Windows
    venv\Scripts\activate
    # On macOS and Linux
    source venv/bin/activate
    ```
4.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
5.  Configure the database connections:
    *   Edit the `ai_sql_assistant/app_secrets.py` file to provide the correct credentials for your Snowflake and PostgreSQL databases.
        *   **Important:** Keep this file secure and do not share it.

## Usage

1.  Run the Streamlit application:
    ```bash
    streamlit run ai_sql_assistant/sql_assistant.py
    ```
2.  Open the application in your browser.
3.  Select the database type (Snowflake or PostgreSQL).
4.  Select the schema.
5.  Enter your natural language query in the text box.
6.  The application will generate and execute the corresponding SQL query and display the results.

## Database Credentials

The database connection details are stored in the `ai_sql_assistant/app_secrets.py` file. You will need to provide the correct credentials for your Snowflake and PostgreSQL databases in this file.

**Snowflake:**

*   `SF_USER`: Your Snowflake username.
*   `SF_PASSWORD`: Your Snowflake password.
*   `SF_ACCOUNT`: Your Snowflake account identifier.
*   `SF_WAREHOUSE`: Your Snowflake warehouse name.
*   `SF_DATABASE`: Your Snowflake database name.
*   `SF_SCHEMA`: Your Snowflake schema name.
*   `SF_ROLE`: Your Snowflake role.

**PostgreSQL:**

*   `PG_HOST`: The host address of your PostgreSQL server.
*   `PG_PORT`: The port number of your PostgreSQL server.
*   `PG_DATABASE`: The name of your PostgreSQL database.
*   `PG_USER`: Your PostgreSQL username.
*   `PG_PASSWORD`: Your PostgreSQL password.

## Notes

*   This application uses a GPT model to generate SQL queries from natural language input. The quality of the generated queries may vary depending on the complexity of the query and the training data used for the model.
*   The application is still under development and may contain bugs or errors.
