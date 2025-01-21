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


def rank_documents(snowflake, query,summarize_folder_path):
    return snowflake.rerank_documents(query,summarize_folder_path)

def get_powershell_code(snowflake, query):
    return snowflake.get_powershell_code(query)


if __name__ == "__main__":
    snowflake = Snowflake()

