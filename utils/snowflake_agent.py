import snowflake.connector
import tempfile
import pandas as pd
import os
import shutil
import streamlit as st
from fpdf import FPDF
from snowflake.core import Root
from snowflake.snowpark import Session

class Snowflake:
    def __init__(self, num_chunks=3):
        snowflake_config = {
            'user': st.secrets["SNOWFLAKE_USER"],
            'password': st.secrets["SNOWFLAKE_PASSWORD"],
            'account': st.secrets["SNOWFLAKE_ACCOUNT"],
            'warehouse': st.secrets["SNOWFLAKE_WAREHOUSE"],
            'database': st.secrets["SNOWFLAKE_DATABASE"],
            'schema': st.secrets["SNOWFLAKE_SCHEMA"]
        }

        conn = snowflake.connector.connect(
                user=snowflake_config['user'],
                password=snowflake_config['password'],
                account=snowflake_config['account'],
                warehouse=snowflake_config['warehouse'],
                database=snowflake_config['database'],
                schema=snowflake_config['schema']
            )
        
        # conn = snowflake.connector.connect(
        #         user="",
        #         password="",
        #         account="",
        #         warehouse="",
        #         database="",
        #         schema=""
        #     )

        cursor = conn.cursor()

        self.conn = conn
        self.cursor = cursor
        self.num_chunks = num_chunks

        connection_parameters = {
            'user':snowflake_config['user'],
            'password':snowflake_config['password'],
            'account':snowflake_config['account'],
            'warehouse':snowflake_config['warehouse'],
            'database':snowflake_config['database'],
            'schema':snowflake_config['schema']
        }
        # connection_parameters = {
        #     'user': '',
        #     'password': '',
        #     'account': '',
        #     'warehouse': '',
        #     'database': '',
        #     'schema': ''
        # }
        
        session = Session.builder.configs(connection_parameters).create()
        self.session = session

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def upload_texts_to_snowflake(self, texts, stage_name="docs", chunk_table_name="docs_chunks_table"):
        """
        Converts a list of text strings to a PDF, uploads it to Snowflake,
        then processes the file to mimic the behavior of the Snowflake task.

        :param texts: List of strings to store in Snowflake.
        :param stage_name: Snowflake stage name to use.
        :param chunk_table_name: Snowflake table to insert processed chunks into.
        """
        try:
            # Step 1: Convert the texts to a PDF
            pdf_filename = tempfile.mktemp(suffix='.pdf')
            self.convert_text_to_pdf('\n'.join(texts), pdf_filename)
            print(f"PDF file created at: {pdf_filename}")

            # Step 2: Ensure the Snowflake stage exists (creates if not already present)
            self.cursor.execute(f"CREATE OR REPLACE STAGE {stage_name};")
            print(f"Snowflake stage '{stage_name}' is ready.")

            # Step 3: Upload the PDF to the Snowflake stage
            self.cursor.execute(f"PUT file://{pdf_filename} @{stage_name} AUTO_COMPRESS = FALSE;")
            print(f"File '{pdf_filename}' successfully uploaded to stage '{stage_name}'.")

            self.cursor.execute("""
                ALTER STAGE docs SET DIRECTORY = (ENABLE = TRUE);
            """)

            input_text = '\n'.join(texts)  # Combine all your texts into a single string

            self.cursor.execute(f"""
                insert into docs_chunks_table (relative_path, size, file_url, scoped_file_url, chunk)
                select 
                    'direct_text' as relative_path,  -- Placeholder for relative_path
                    LENGTH('{input_text}') as size,  -- Calculate the size of the input text
                    'your_file_url' as file_url,  -- Provide the file URL (use placeholder or actual URL)
                    build_scoped_file_url(@docs, 'direct_text') as scoped_file_url,
                    chunk as chunk  -- Get the chunk from the function
                from 
                    table(text_chunker('{input_text}'))  -- Call your custom function here
            """)

            print(f"Data successfully processed and loaded into '{chunk_table_name}'.")

        except Exception as e:
            print(f"Error during upload: {e}")
            self.conn.rollback()

        finally:
            # Step 5: Cleanup - Delete the temporary PDF file
            try:
                if os.path.exists(pdf_filename):
                    os.remove(pdf_filename)
                    print(f"Temporary PDF file '{pdf_filename}' has been deleted.")
            except Exception as cleanup_error:
                print(f"Error during cleanup: {cleanup_error}")


    def convert_text_to_pdf(self, text, pdf_filename):
        """Converts a text string to a PDF and saves it."""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, text)
        pdf.output(pdf_filename)


    def create_prompt(self, myquestion):
        root = Root(self.session)
        svc = root.databases["CC_QUICKSTART_CORTEX_SEARCH_DOCS"].schemas["DATA"].cortex_search_services["CC_SEARCH_SERVICE_CS"]
        COLUMNS = [
            "chunk",
            "relative_path",
        ]
        prompt_context = svc.search(myquestion, COLUMNS, limit=5).json()
        print(prompt_context)
        
        prompt = f"""
           You are an expert chat assistance that extracs information from the CONTEXT provided
           between <context> and </context> tags.
           When ansering the question contained between <question> and </question> tags
           be concise and do not hallucinate. 
           If you don't have the information just say so.
           Only anwer the question if you can extract it from the CONTEXT provideed.
           
           Do not mention the CONTEXT used in your answer.
    
           <context>          
           {prompt_context}
           </context>
           <question>  
           {myquestion}
           </question>
           Answer: 
           """

        # json_data = json.loads(prompt_context)

        print("prompt created")

        print(prompt)

        # relative_paths = set(item['relative_path'] for item in json_data['results'])
     
        return prompt
    
    def get_answer_from_rag(self, myquestion, model_name='mistral-large'):
        prompt = self.create_prompt(myquestion)

        query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{model_name}',
                $$ {prompt} $$
            ) AS REFINED_QUERY;
        """

        try:
            self.cursor.execute(query)
            return self.cursor.fetchone()[0]
        except Exception as e:
            return f"Error: {e}"

    def get_powershell_code(self, myquestion):
        prompt = f"""
                Write a powershell script based on the Input (Task Description) given.

                ### Input (Task Description):
                {myquestion}

                ### Output (PowerShell Code):
                
        """

        query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                $$ {prompt} $$
            ) AS REFINED_QUERY;
        """

        try:
            self.cursor.execute(query)
            return self.cursor.fetchone()[0]
        except Exception as e:
            return f"Error: {e}"
        
    def summarise(self, file_paths,temp_path):
        summary_folder = f"{temp_path}/summarize"
        os.makedirs(summary_folder, exist_ok=True)
        for i, file_path in enumerate(file_paths):
            with open(file_path, 'r') as f:
                text = f.read()
                summary = self.summarize_text(text)
                with open(os.path.join(summary_folder, f"{i}.txt"), 'w') as f:
                    f.write(summary)
        return summary_folder
                
    # def summarise(self, input_dir="/content/output/"):
    #     summarize_folder = input_dir+"summarize"
    #     os.makedirs(summarize_folder, exist_ok=True)
    #     tot = []
    #     for i in os.walk(input_dir):
    #         if i[2]:
    #             for file in i[2]:
    #                 if file.endswith(".txt"):
    #                     full_file_path = os.path.join(i[0], file)
    #                     doc_id = i[0].split("/")[-1] + "_" + file.split(".")[0]
    #                     new_file_path = os.path.join(summarize_folder, doc_id + ".txt")
    #                     shutil.move(full_file_path, new_file_path)
    #                     doc_map = (doc_id, new_file_path)
    #                     tot.append(doc_map)

    #     # all the unsummarized-text files are under /content/output/summarize/

    #     for file in os.listdir(summarize_folder):
    #         with open(os.path.join(summarize_folder, file), 'r') as f:
    #             text = f.read()
    #             summary = self.summarize_text(text)
    #             with open(os.path.join(summarize_folder, file), 'w') as f:
    #                 f.write(summary)
    
    def summarize_text(self, text):
        query = f"""
            SELECT SNOWFLAKE.CORTEX.SUMMARIZE(
                $$ {text} $$
            ) AS SUMMARY;
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchone()[0]
        except Exception as e:
            return f"Error: {e}"
        
    def query_refiner(self, search_query):
        prompt = f"""
            Given the following user query, refine it to make it more specific, clear, and actionable, ensuring it avoids ambiguity and aligns with the user's likely intent. Provide the refined query in less than 25 words below:

            Original Query: {search_query}

            Refined Query:
        """
        query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                $$ {prompt} $$
            ) AS REFINED_QUERY;
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchone()[0]
        except Exception as e:
            return f"Error: {e}"

    def rerank_documents(self, search_query,file_dir,top_k=3):
        try:
            self.cursor.execute("""
                CREATE OR REPLACE TEMPORARY TABLE temp_text_files (
                    id INT,
                    content VARCHAR
                );
            """)
            print("Temporary table created.")

            text_files = [f for f in os.listdir(file_dir)]
            print(len(text_files))
            for idx, file in enumerate(text_files, start=1):
                file_path = os.path.join(file_dir, file)
                with open(file_path, 'r') as f:
                    text = f.read()
                    self.cursor.execute("INSERT INTO temp_text_files (id, content) VALUES (%s, %s);", (idx, text))
            print(f"{len(text_files)} text files inserted into the temporary table.")

            query_ranking = """
                WITH query_embedding AS (
                    SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s) AS embedding
                )
                SELECT 
                    id,
                    content,
                    VECTOR_COSINE_SIMILARITY(
                        query_embedding.embedding, 
                        SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', content)
                    ) AS similarity_score
                FROM temp_text_files, query_embedding
                ORDER BY similarity_score DESC
                LIMIT %s;
            """

            self.cursor.execute(query_ranking, (search_query, top_k))
            ranked_results = self.cursor.fetchall()
            return ranked_results
        
        except Exception as e:
            print(f"Error: {e}")
            raise
        
        finally:
            self.cursor.execute("DROP TABLE IF EXISTS temp_text_files;")
            print("Temporary table dropped.")

    def get_user_friendly_responses(self, doc):
        prompt = f"""
            Based on the context: {doc}, create a clear, step-by-step guide for non-technical users. Break down the process into manageable steps.

            User-Friendly Guide:
        """
        query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                $$ {prompt} $$
            ) AS REFINED_QUERY;
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchone()[0]
        except Exception as e:
            return f"Error: {e}"


# example usage
if __name__ == "__main__":
    snowflake = Snowflake()
    snowflake.upload_texts_to_snowflake(["This is a test document."])
    #initialise the web bots