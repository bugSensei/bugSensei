import streamlit as st
import snowflake.connector
import pandas as pd

pd.set_option("max_colwidth", None)
num_chunks = 3

def get_snowflake_connection(snowflake_config):
    """Establishes a connection to Snowflake using the Snowflake connector."""
    return snowflake.connector.connect(
        user=snowflake_config['user'],
        password=snowflake_config['password'],
        account=snowflake_config['account'],
        warehouse=snowflake_config['warehouse'],
        database=snowflake_config['database'],
        schema=snowflake_config['schema']
    )

def create_prompt(conn, myquestion):
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

    cursor = conn.cursor()
    cursor.execute(cmd, (myquestion, num_chunks))
    df_context = pd.DataFrame(cursor.fetchall(), columns=["chunk", "relative_path"])

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
    cursor.execute(cmd2)
    df_url_link = pd.DataFrame(cursor.fetchall(), columns=["URL_LINK"])
    url_link = df_url_link["URL_LINK"].iloc[0]

    return prompt, url_link, relative_path

def complete(conn, myquestion, model_name='mistral-large'):
    prompt, url_link, relative_path = create_prompt(conn, myquestion)
    cmd = "SELECT SNOWFLAKE.CORTEX.COMPLETE(?, ?) AS RESPONSE;"

    cursor = conn.cursor()
    cursor.execute(cmd, (model_name, prompt))
    response = cursor.fetchone()[0]

    return response, url_link, relative_path

def display_response(conn, question, model='mistral-7b'):
    response, url_link, relative_path = complete(conn, question, model)
    st.markdown(response)
    if rag == 1:
        display_url = f"Link to [{relative_path}]({url_link}) that may be useful"
        st.markdown(display_url)

# Main code
st.title("Asking Questions to Your Own Documents with Snowflake Cortex:")
st.write("""You can ask questions and decide if you want to use your documents for context or allow the model to create its own response.""")
st.write("This is the list of documents you already have:")

# Snowflake connection configuration
snowflake_config = {
    'user': 'YOUR_USERNAME',
    'password': 'YOUR_PASSWORD',
    'account': 'YOUR_ACCOUNT',
    'warehouse': 'XS_WH',
    'database': 'CC_QUICKSTART_CORTEX_DOCS',
    'schema': 'DATA'
}

conn = get_snowflake_connection(snowflake_config)

cursor = conn.cursor()
cursor.execute("LS @docs;")

list_docs = [doc[0] for doc in cursor.fetchall()]
st.dataframe(list_docs)

# LLM selection
model = st.sidebar.selectbox('Select your model:', (
    'mixtral-8x7b',
    'snowflake-arctic',
    'mistral-large',
    'llama3-8b',
    'llama3-70b',
    'reka-flash',
    'mistral-7b',
    'llama2-70b-chat',
    'gemma-7b'
))

question = st.text_input("Enter question", placeholder="Is there any special lubricant to be used with the premium bike?", label_visibility="collapsed")
rag = st.sidebar.checkbox('Use your own documents as context?')

use_rag = 1 if rag else 0

if question:
    display_response(conn, question, model, use_rag)

# Close connection when done
conn.close()
