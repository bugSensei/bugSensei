import os

#pip install snowflake-python-connector
import snowflake.connector

def upload_texts_to_snowflake(texts, file_name, table_name, stage_name, snowflake_config, cursor):
    """
    Converts a list of text strings to a text file and uploads it to Snowflake.

    :param texts: List of strings to store in Snowflake.
    :param file_name: Name of the text file to create (e.g., 'texts.txt').
    :param table_name: Snowflake table name to upload data to.
    :param stage_name: Snowflake stage name to use.
    :param snowflake_config: Dictionary containing Snowflake connection details.
    :param cursor: Snowflake cursor object. (after establishing snowflake connection using snowflake_config)
    """
    # Step 1: Write texts to a file
    with open(file_name, 'w') as file:
        file.write('\n'.join(texts))
    
    print(f"Text file '{file_name}' created successfully.")

    try:
        # Step 2: Connect to Snowflake
        conn = snowflake.connector.connect(
            user=snowflake_config['user'],
            password=snowflake_config['password'],
            account=snowflake_config['account'],
            warehouse=snowflake_config['warehouse'],
            database=snowflake_config['database'],
            schema=snowflake_config['schema']
        )
        cursor = conn.cursor()
        
        # Step 3: Create stage if not exists
        cursor.execute(f"CREATE OR REPLACE STAGE {stage_name};")
        print(f"Stage '{stage_name}' ready.")
        
        # Step 4: Upload file to Snowflake stage
        cursor.execute(f"PUT file://{os.path.abspath(file_name)} @{stage_name};")
        print(f"File '{file_name}' uploaded to stage '{stage_name}'.")
        
        # Step 5: Load data into the table
        cursor.execute(f"""
            COPY INTO {table_name}(text_content)
            FROM @{stage_name}/{file_name}
            FILE_FORMAT = (TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '"' FIELD_DELIMITER = '\n');
        """)
        print(f"Data loaded into table '{table_name}'.")

    except Exception as e:
        print("Error:", e)

    finally:
        # Cleanup
        cursor.close()
        conn.close()
        if os.path.exists(file_name):
            os.remove(file_name)
        print("Cleanup complete.")

# Example usage
texts = [
    "This is the first string.",
    "Another line of text.",
    "Yet another string to upload."
]

snowflake_config = {
    'user': 'YOUR_USERNAME',
    'password': 'YOUR_PASSWORD',
    'account': 'YOUR_ACCOUNT',
    'warehouse': 'YOUR_WAREHOUSE',
    'database': 'YOUR_DATABASE',
    'schema': 'YOUR_SCHEMA'
}

upload_texts_to_snowflake(
    texts=texts,
    file_name='texts.txt',
    table_name='text_warehouse',
    stage_name='my_stage',
    snowflake_config=snowflake_config
)
