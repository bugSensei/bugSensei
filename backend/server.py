import os
import json
import streamlit as st
from utils.snowflake_agent import Snowflake

from utils import eurus
# unsummarized files under /content/output/summarize -- refer utils/snowflake_agent.py
def web_search(snowflake, search_query,eurus,temp_path):
    try:
        eurus.get_extracted_results(search_query)   
    except Exception as e:
        print("Web Extraction Failed !",e)
    snowflake.summarise(temp_path + "/")

def snowflake_retrieval(snowflake, search_query):
    response = snowflake.get_answer_from_rag(search_query)
    return response

def query_refiner(snowflake, search_query):
    refined_query = snowflake.query_refiner(search_query)
    return refined_query

def upload_files_to_snowflake(snowflake, dir_path):
    texts = []
    for file in os.listdir(dir_path):
        with open(os.path.join(dir_path, file), 'r') as f:
            text = f.read()
            texts.append(text)
            
    snowflake.upload_texts_to_snowflake(texts)


def rank_documents(snowflake, query,summarize_folder_path, temp_path):
    texts = snowflake.rerank_documents(query,summarize_folder_path)
    # reranked_file_path = f"{temp_path}/reranked"
    # os.makedirs(reranked_file_path, exist_ok=True)
    # print("ranked documents")
    # for i, text in enumerate(texts):
    #     print("Index",i)
    #     print("Text",text)
    #     with open(f"{reranked_file_path}/reranked_{i}.txt", "w") as f:
    #         print(text)
    #         f.write(text)

    return texts

def get_user_friendly_responses(snowflake, docs):
    user_docs = []
    for doc in docs:
        user_doc = snowflake.get_user_friendly_responses(doc)
        user_docs.append(user_doc)
    return user_docs
    #return snowflake.get_user_friendly_responses(query)

def get_powershell_code(snowflake, query):
    return snowflake.get_powershell_code(query)


if __name__ == "__main__":
    snowflake = Snowflake()

