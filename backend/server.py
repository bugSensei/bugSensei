import snowflake.connector
import tempfile
import pandas as pd
import os

class Snowflake:
    def __init__(self, num_chunks=3):
        snowflake_config = {
            'user': 'YOUR_USERNAME',
            'password': 'YOUR_PASSWORD',
            'account': 'YOUR_ACCOUNT',
            'warehouse': 'YOUR_WAREHOUSE',
            'database': 'YOUR_DATABASE',
            'schema': 'YOUR_SCHEMA'
        }

        conn = snowflake.connector.connect(
                user=snowflake_config['user'],
                password=snowflake_config['password'],
                account=snowflake_config['account'],
                warehouse=snowflake_config['warehouse'],
                database=snowflake_config['database'],
                schema=snowflake_config['schema']
            )
        cursor = conn.cursor()

        self.conn = conn
        self.cursor = cursor
        self.num_chunks = num_chunks

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def upload_texts_to_snowflake(self, texts, table_name, stage_name):
        """
        Converts a list of text strings to a temporary text file and uploads it to Snowflake.

        :param texts: List of strings to store in Snowflake.
        :param table_name: Snowflake table name to upload data to.
        :param stage_name: Snowflake stage name to use.
        """
        try:
            # Step 1: Create a temporary file to store the text data
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
                temp_file.write('\n'.join(texts))
                temp_file_path = temp_file.name 
            print(f"Temporary file created at: {temp_file_path}")

            # Step 2: Ensure the Snowflake stage exists (creates if not already present)
            self.cursor.execute(f"CREATE OR REPLACE STAGE {stage_name};")
            print(f"Snowflake stage '{stage_name}' is ready.")

            # Step 3: Upload the temporary file to the Snowflake stage
            self.cursor.execute(f"PUT file://{temp_file_path} @{stage_name};")
            print(f"File '{temp_file_path}' successfully uploaded to stage '{stage_name}'.")

            # Step 4: Copy the data from the stage into the target table
            self.cursor.execute(f"""
                COPY INTO {table_name}(text_content)
                FROM @{stage_name}/{os.path.basename(temp_file_path)}
                FILE_FORMAT = (TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '"' FIELD_DELIMITER = '\n');
            """)
            print(f"Data successfully loaded into Snowflake table '{table_name}'.")

        except Exception as e:
            print(f"Error during upload: {e}")
            self.conn.rollback() 

        finally:
            # Step 5: Cleanup - Delete the temporary file
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    print(f"Temporary file '{temp_file_path}' has been deleted.")
            except Exception as cleanup_error:
                print(f"Error during cleanup: {cleanup_error}")


    def create_prompt(self, myquestion):
        cmd = """
        WITH results AS (
            SELECT RELATIVE_PATH,
                    VECTOR_COSINE_SIMILARITY(docs_chunks_table.chunk_vec,
                    SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', ?)) AS similarity,
                    chunk
            FROM docs_chunks_table
            ORDER BY similarity DESC
            LIMIT ?
        )
        SELECT chunk, relative_path FROM results;
        """

        self.cursor.execute(cmd, (myquestion, self.num_chunks))
        df_context = pd.DataFrame(self.cursor.fetchall(), columns=["chunk", "relative_path"])

        prompt_context = "".join(df_context["chunk"][:-1]).replace("'", "")
        relative_path = df_context["relative_path"].iloc[0]

        prompt = f"""
        You are an expert assistant extracting information from the context provided. 
        Answer the question based on the context. Be concise and do not hallucinate. 
        If you don't have the information, just say so.
        Context: {prompt_context}
        Question: {myquestion}
        Answer:
        """

        cmd2 = f"SELECT GET_PRESIGNED_URL(@docs, '{relative_path}', 360) AS URL_LINK FROM directory(@docs);"
        self.cursor.execute(cmd2)

        return prompt, relative_path

    def get_answer_from_rag(self, myquestion, model_name='mistral-large'):
        prompt, relative_path = self.create_prompt(myquestion)
        cmd = "SELECT SNOWFLAKE.CORTEX.COMPLETE(?, ?) AS RESPONSE;"

        self.cursor.execute(cmd, (model_name, prompt))
        response = self.cursor.fetchone()[0]

        return response
    

if __name__ == "__main__":
    snowflake = Snowflake()
    #initialise the web bots