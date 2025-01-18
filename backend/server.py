import os
import json
import streamlit as st
from utils.snowflake_agent import Snowflake

from utils import eurus
# unsummarized files under /content/output/summarize -- refer utils/snowflake_agent.py
def web_search(snowflake, search_query):
    try:
        wt = eurus.Eurus()
        wt.get_extracted_results(search_query)   
    except Exception as e:
        print("Web Extraction Failed !",e)

    snowflake.summarise()

def snowflake_retrieval(snowflake, search_query):
    snowflake.get_answer_from_rag(search_query)
    return snowflake.get_answer_from_rag(search_query)

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


def rank_documents(snowflake, query):
    return snowflake.rerank_documents(query)


if __name__ == "__main__":
    snowflake = Snowflake()

